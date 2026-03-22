"""Automated tests for the main MCP server flows."""

from pathlib import Path
import shutil
import unittest
from uuid import uuid4

from project.database import Database
from project.embeddings import EmbeddingService
from project.models import AppDependencies, CreateUserResponse, ErrorResponse, SearchUserMatch, UserRecord
from project.server import create_app
from project.vector_store import VectorStore


class MCPServerFlowTests(unittest.IsolatedAsyncioTestCase):
    """Validate the current MCP tools and their core behaviors."""

    def setUp(self) -> None:
        self.temp_root = Path.cwd() / ".tmp" / "test-workspaces"
        self.temp_root.mkdir(parents=True, exist_ok=True)
        self.base_dir = self.temp_root / f"test-{uuid4().hex}"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.dependencies = AppDependencies(
            database=Database(str(self.base_dir / "test.sqlite3")),
            embedding_service=EmbeddingService(),
            vector_store=VectorStore(self.base_dir / "faiss_index"),
        )
        self.app = create_app(self.dependencies)

    def tearDown(self) -> None:
        shutil.rmtree(self.base_dir, ignore_errors=True)

    async def test_create_user_tool_persists_and_indexes_user(self) -> None:
        create_user = await self.app.get_tool("create_user")

        result = create_user.fn(
            name="Ana",
            email="ana@test.com",
            description="cliente premium com automacao financeira",
        )

        self.assertIsInstance(result, CreateUserResponse)
        stored_user = self.dependencies.database.get_user_by_id(result.id)
        self.assertIsNotNone(stored_user)
        self.assertEqual(stored_user.email, "ana@test.com")
        self.assertEqual(self.dependencies.vector_store.get_user_id_for_vector(0), result.id)

    async def test_create_user_tool_returns_validation_error_for_duplicate_email(self) -> None:
        create_user = await self.app.get_tool("create_user")
        create_user.fn(
            name="Ana",
            email="ana@test.com",
            description="cliente premium com automacao financeira",
        )

        duplicate = create_user.fn(
            name="Ana 2",
            email="ana@test.com",
            description="cliente duplicado",
        )

        self.assertIsInstance(duplicate, ErrorResponse)
        self.assertEqual(duplicate.code, "validation_error")

    async def test_get_user_tool_returns_existing_user(self) -> None:
        create_user = await self.app.get_tool("create_user")
        get_user = await self.app.get_tool("get_user")
        created = create_user.fn(
            name="Bruno",
            email="bruno@test.com",
            description="cliente com foco operacional",
        )

        result = get_user.fn(user_id=created.id)

        self.assertIsInstance(result, UserRecord)
        self.assertEqual(result.id, created.id)
        self.assertEqual(result.email, "bruno@test.com")

    async def test_get_user_tool_returns_not_found_for_missing_user(self) -> None:
        get_user = await self.app.get_tool("get_user")

        result = get_user.fn(user_id=999)

        self.assertIsInstance(result, ErrorResponse)
        self.assertEqual(result.code, "not_found")

    async def test_search_users_tool_returns_semantic_matches(self) -> None:
        create_user = await self.app.get_tool("create_user")
        search_users = await self.app.get_tool("search_users")

        create_user.fn(
            name="Carla",
            email="carla@test.com",
            description="responsavel por operacoes financeiras e automacao de cobranca",
        )
        create_user.fn(
            name="Diego",
            email="diego@test.com",
            description="coordena suporte tecnico industrial e atendimento de campo",
        )
        create_user.fn(
            name="Eva",
            email="eva@test.com",
            description="lidera automacao de processos comerciais e qualificacao de leads",
        )

        results = search_users.fn(query="automacao financeira premium", top_k=3)

        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 2)
        self.assertIsInstance(results[0], SearchUserMatch)
        self.assertEqual(results[0].name, "Carla")
        self.assertGreaterEqual(results[0].score, results[1].score)

    async def test_search_users_tool_downranks_generic_cliente_term(self) -> None:
        create_user = await self.app.get_tool("create_user")
        search_users = await self.app.get_tool("search_users")

        create_user.fn(
            name="Ana",
            email="ana@test.com",
            description="especialista em analise de dados financeiros e indicadores de desempenho",
        )
        create_user.fn(
            name="Bruno",
            email="bruno@test.com",
            description="cliente com foco em operacao interna e rotinas administrativas",
        )

        results = search_users.fn(query="Cliente com capacidade analítica", top_k=2)

        self.assertIsInstance(results, list)
        self.assertEqual(results[0].name, "Ana")
        self.assertGreater(results[0].score, results[1].score)

    async def test_search_users_tool_validates_top_k(self) -> None:
        search_users = await self.app.get_tool("search_users")

        result = search_users.fn(query="automacao", top_k=0)

        self.assertIsInstance(result, ErrorResponse)
        self.assertEqual(result.code, "validation_error")


if __name__ == "__main__":
    unittest.main()
