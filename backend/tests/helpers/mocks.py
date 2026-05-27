"""In-memory fakes for unit and integration tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from app.domain.entities.document import Document, DocumentStatus
from app.domain.entities.organization import Organization
from app.domain.entities.organization_membership import OrganizationMembership
from app.domain.entities.user import User
from app.domain.value_objects.membership_status import MembershipStatus


@dataclass
class FakeUserRepo:
    by_email: dict[str, User] = field(default_factory=dict)
    by_id: dict[UUID, User] = field(default_factory=dict)
    created: list[User] = field(default_factory=list)

    async def get_user_by_email(self, *, email: str) -> User | None:
        return self.by_email.get(email.lower())

    async def create_user(self, *, user: User) -> User:
        self.by_email[user.email.lower()] = user
        self.by_id[user.id] = user
        self.created.append(user)
        return user

    async def update_last_login(self, *, user_id: UUID) -> None:
        user = self.by_id.get(user_id)
        if user:
            user.last_login_at = user.last_login_at


@dataclass
class FakeOrgRepo:
    slugs: set[str] = field(default_factory=set)
    orgs: dict[UUID, Organization] = field(default_factory=dict)

    async def exists_slug(self, *, slug: str) -> bool:
        return slug in self.slugs

    async def create_org(self, *, org: Organization) -> Organization:
        self.slugs.add(org.slug)
        self.orgs[org.id] = org
        return org


@dataclass
class FakeMembershipRepo:
    memberships: list[OrganizationMembership] = field(default_factory=list)

    async def create_membership(
        self, *, membership: OrganizationMembership
    ) -> OrganizationMembership:
        self.memberships.append(membership)
        return membership

    async def get_active_membership(
        self, *, user_id: UUID, org_id: UUID
    ) -> OrganizationMembership | None:
        for m in self.memberships:
            if (
                m.user_id == user_id
                and m.org_id == org_id
                and m.status == MembershipStatus.ACTIVE
            ):
                return m
        return None

    async def get_membership_by_org_slug(
        self, *, org_slug: str, user_id: UUID
    ) -> OrganizationMembership | None:
        return self.memberships[0] if self.memberships else None

    async def list_user_memberships(
        self, *, user_id: UUID
    ) -> list[OrganizationMembership]:
        return [m for m in self.memberships if m.user_id == user_id]


class FakeUoW:
    def __init__(
        self,
        *,
        users: FakeUserRepo | None = None,
        organizations: FakeOrgRepo | None = None,
        memberships: FakeMembershipRepo | None = None,
    ) -> None:
        self.users = users or FakeUserRepo()
        self.organizations = organizations or FakeOrgRepo()
        self.memberships = memberships or FakeMembershipRepo()
        self.committed = False

    async def __aenter__(self) -> FakeUoW:
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        pass


def uow_factory(uow: FakeUoW):
    def _factory() -> FakeUoW:
        return uow

    return _factory


@dataclass
class FakeDocumentRepo:
    documents: dict[UUID, Document] = field(default_factory=dict)
    by_checksum: dict[tuple[UUID, str], Document] = field(default_factory=dict)

    async def save(self, document: Document) -> Document:
        self.documents[document.id] = document
        if document.checksum:
            self.by_checksum[(document.org_id, document.checksum)] = document
        return document

    async def find_by_checksum(self, *, org_id: UUID, checksum: str) -> Document | None:
        return self.by_checksum.get((org_id, checksum))

    async def update_status(
        self,
        *,
        document_id: UUID,
        status: str,
        error_message: str | None = None,
        chunk_count: int | None = None,
        token_count: int | None = None,
    ) -> None:
        doc = self.documents.get(document_id)
        if doc:
            doc.status = DocumentStatus(status)
            if error_message is not None:
                doc.error_message = error_message
            if chunk_count is not None:
                doc.chunk_count = chunk_count
            if token_count is not None:
                doc.token_count = token_count

    async def get_by_id(self, *, document_id: UUID, org_id: UUID) -> Document | None:
        doc = self.documents.get(document_id)
        if doc and doc.org_id == org_id:
            return doc
        return None

    async def list_by_org_id(
        self,
        *,
        org_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> tuple[list[Document], int]:
        items = [d for d in self.documents.values() if d.org_id == org_id]
        if status:
            items = [d for d in items if d.status.value == status]
        total = len(items)
        start = (page - 1) * page_size
        return items[start : start + page_size], total

    async def delete(self, *, document_id: UUID, org_id: UUID) -> None:
        doc = self.documents.pop(document_id, None)
        if doc and doc.checksum:
            self.by_checksum.pop((org_id, doc.checksum), None)

    def count_by_org(self, org_id: str) -> int:
        oid = UUID(org_id) if isinstance(org_id, str) else org_id
        return sum(1 for d in self.documents.values() if d.org_id == oid)

    def count_failed_by_org(self, org_id: str) -> int:
        oid = UUID(org_id) if isinstance(org_id, str) else org_id
        return sum(
            1
            for d in self.documents.values()
            if d.org_id == oid and d.status == DocumentStatus.FAILED
        )


@dataclass
class FakeChunkRepo:
    chunks: list[Any] = field(default_factory=list)

    async def list_by_document(self, *, document_id: UUID) -> list:
        return [c for c in self.chunks if c.document_id == document_id]

    def count_by_org(self, org_id: str) -> int:
        oid = UUID(org_id) if isinstance(org_id, str) else org_id
        return sum(1 for c in self.chunks if c.org_id == oid)


@dataclass
class FakeSyncDocumentRepo:
    documents: dict[UUID, Document] = field(default_factory=dict)

    def get_by_id(self, *, document_id: UUID) -> Document | None:
        return self.documents.get(document_id)

    def update_status(
        self,
        *,
        document_id: UUID,
        status: str,
        error_message: str | None = None,
        chunk_count: int | None = None,
        token_count: int | None = None,
    ) -> None:
        doc = self.documents.get(document_id)
        if doc:
            doc.status = DocumentStatus(status)
            if error_message is not None:
                doc.error_message = error_message
            if chunk_count is not None:
                doc.chunk_count = chunk_count
            if token_count is not None:
                doc.token_count = token_count


@dataclass
class FakeSyncChunkRepo:
    chunks: list[Any] = field(default_factory=list)

    def add_many(self, chunks: list) -> None:
        self.chunks.extend(chunks)

    def delete_by_document(self, *, document_id: UUID) -> None:
        self.chunks = [c for c in self.chunks if c.document_id != document_id]


class FakeMemoryStorage:
    """Minimal ObjectStorage fake."""

    def __init__(self) -> None:
        self._objects: dict[str, bytes] = {}

    def put_object(
        self, *, key: str, data: bytes, content_type: str | None = None
    ) -> str:
        self._objects[key] = data
        return key

    def get_object(self, *, key: str) -> bytes:
        return self._objects[key]

    def delete_object(self, *, key: str) -> None:
        self._objects.pop(key, None)


class FakeEmbedder:
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


class FakeVectorStore:
    def __init__(self) -> None:
        self.upserted: list[dict] = []

    async def upsert(self, *, vectors: list, namespace: str) -> None:
        self.upserted.append({"vectors": vectors, "namespace": namespace})

    async def query_by_similarity(self, **kwargs: Any) -> list[dict]:
        return []

    async def delete_by_document_id(self, *, document_id: str, namespace: str) -> None:
        pass


def make_document(
    *,
    org_id: UUID | None = None,
    status: DocumentStatus = DocumentStatus.PENDING,
    storage_key: str = "org/doc.txt",
    source_type: str = "text",
) -> Document:
    doc_id = uuid4()
    oid = org_id or uuid4()
    return Document(
        id=doc_id,
        org_id=oid,
        title="test-doc",
        source_type=source_type,
        storage_url=storage_key,
        checksum="abc",
        status=status,
    )
