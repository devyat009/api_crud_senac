def seed_categories(base_url: str, total: int = 50) -> None:
	print(f"\n[categorias] Alvo: {total} categorias @ {base_url}")
	endpoint = f"{PRODUCT_ENDPOINT}/category"
	criados = 0
	falhas = 0
	with httpx.Client(base_url=base_url, timeout=20.0) as client:
		for idx in range(total):
			nome = f"Categoria Stress {idx + 1} {uuid.uuid4().hex[:6]}"
			payload = {"nome_categoria": nome}
			try:
				response = client.post(endpoint, json=payload)
				if response.status_code == 200:
					body = response.json()
					if body.get("success"):
						criados += 1
					else:
						falhas += 1
						print(f"[categorias] #{idx + 1} rejeitada: {body.get('message')}")
				else:
					falhas += 1
					print(f"[categorias] #{idx + 1} HTTP {response.status_code}: {response.text}")
			except Exception as exc:
				falhas += 1
				print(f"[categorias] #{idx + 1} exceção: {exc}")
	print(f"[categorias] Finalizado. Criadas: {criados}, Falhas: {falhas}\n")

def seed_brands(base_url: str, total: int = 50) -> None:
	print(f"\n[marcas] Alvo: {total} marcas @ {base_url}")
	endpoint = f"{PRODUCT_ENDPOINT}/brand"
	criados = 0
	falhas = 0
	with httpx.Client(base_url=base_url, timeout=20.0) as client:
		for idx in range(total):
			nome = f"Marca Stress {idx + 1} {uuid.uuid4().hex[:6]}"
			payload = {"nome_marca": nome}
			try:
				response = client.post(endpoint, json=payload)
				if response.status_code == 200:
					body = response.json()
					if body.get("success"):
						criados += 1
					else:
						falhas += 1
						print(f"[marcas] #{idx + 1} rejeitada: {body.get('message')}")
				else:
					falhas += 1
					print(f"[marcas] #{idx + 1} HTTP {response.status_code}: {response.text}")
			except Exception as exc:
				falhas += 1
				print(f"[marcas] #{idx + 1} exceção: {exc}")
	print(f"[marcas] Finalizado. Criadas: {criados}, Falhas: {falhas}\n")
"""Menu utilitário para estressar os endpoints de Produto e Cliente."""

import os
import random
import uuid
from datetime import date, timedelta
from typing import Any, Dict, List

import httpx


DEFAULT_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
PRODUCT_ENDPOINT = "/api/v1/products"
CLIENT_ENDPOINT = "/api/v1/clientes"
PRODUCT_TOTAL = 50
CLIENT_TOTAL = 50

PRODUCT_NAMES = [
	"Widget",
	"Gadget",
	"Dispositivo",
	"Instrumento",
	"Acessório",
	"Módulo",
	"Componente",
	"Ferramenta",
]
PRODUCT_MODELS = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Omega", "Prime", "Ultra"]
PRODUCT_COLORS = ["Azul", "Vermelho", "Verde", "Amarelo", "Preto", "Branco", "Cinza", "Roxo"]
PRODUCT_SIZES = ["PP", "P", "M", "G", "GG", "Padrão"]
PRODUCT_DESCRIPTIONS = [
	"Item de lote para teste de estresse",
	"Produto gerado automaticamente",
	"Amostra de cenário de performance",
	"Registro de preenchimento de estoque",
	"Entrada sintética de catálogo",
]
PRODUCT_OBSERVATIONS = [
	"Gerado pelo script de estresse",
	"Importação em lote",
	"Dados de teste QA",
	"Não promover",
	"Dados descartáveis",
]

CLIENT_FIRST_NAMES = [
	"Alex",
	"Jordan",
	"Taylor",
	"Morgan",
	"Casey",
	"Sam",
	"Charlie",
	"Riley",
]
CLIENT_LAST_NAMES = [
	"Silva",
	"Santos",
	"Oliveira",
	"Souza",
	"Lima",
	"Costa",
	"Pereira",
	"Ferreira",
]
CLIENT_PROFILES = ["bronze", "prata", "ouro", "platina", "vip"]
STREET_NAMES = ["Rua das Flores", "Avenida Brasil", "Rua do Comércio", "Travessa Central", "Rua da Paz", "Alameda Verde"]
CITIES = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Porto Alegre", "Recife"]


def random_digits(length: int) -> str:
	return str(random.randint(10 ** (length - 1), (10 ** length) - 1))


def random_date(start_year: int = 1965, end_year: int = 2005) -> str:
	start = date(start_year, 1, 1)
	end = date(end_year, 12, 31)
	delta_days = (end - start).days
	chosen = start + timedelta(days=random.randint(0, delta_days))
	return chosen.isoformat()


def ensure_categories(client: httpx.Client, target: int = 5) -> List[str]:
	categories_url = f"{PRODUCT_ENDPOINT}/category"
	category_ids: List[str] = []

	try:
		response = client.get(categories_url)
		if response.status_code == 200:
			payload = response.json()
			if payload.get("success"):
				category_ids = [item["id_category"] for item in payload.get("data", [])]
	except Exception as exc:
		print(f"[category] fetch failed: {exc}")

	while len(category_ids) < target:
		name = f"Stress Category {uuid.uuid4().hex[:6]}"
		try:
			creation = client.post(categories_url, json={"nome_categoria": name})
			if creation.status_code == 200:
				data = creation.json()
				if data.get("success"):
					category_ids.append(data["data"]["id_category"])
				else:
					print(f"[category] creation rejected: {data.get('message')}")
			else:
				print(f"[category] HTTP {creation.status_code} while creating {name}")
				break
		except Exception as exc:
			print(f"[category] exception while creating {name}: {exc}")
			break

	return category_ids


def ensure_brands(client: httpx.Client, target: int = 5) -> List[str]:
	brands_url = f"{PRODUCT_ENDPOINT}/brand"
	brand_ids: List[str] = []

	try:
		response = client.get(brands_url)
		if response.status_code == 200:
			payload = response.json()
			if payload.get("success"):
				brand_ids = [item["id_brand"] for item in payload.get("data", [])]
	except Exception as exc:
		print(f"[brand] fetch failed: {exc}")

	while len(brand_ids) < target:
		name = f"Stress Brand {uuid.uuid4().hex[:6]}"
		try:
			creation = client.post(brands_url, json={"nome_marca": name})
			if creation.status_code == 200:
				data = creation.json()
				if data.get("success"):
					brand_ids.append(data["data"]["id_brand"])
				else:
					print(f"[brand] creation rejected: {data.get('message')}")
			else:
				print(f"[brand] HTTP {creation.status_code} while creating {name}")
				break
		except Exception as exc:
			print(f"[brand] exception while creating {name}: {exc}")
			break

	return brand_ids


def build_product_payload(index: int, categories: List[str], brands: List[str]) -> Dict[str, Any]:
	category_id = random.choice(categories)
	brand_id = random.choice(brands)
	nome = random.choice(PRODUCT_NAMES)
	modelo = random.choice(PRODUCT_MODELS)
	descricao = random.choice(PRODUCT_DESCRIPTIONS)
	observacao = random.choice(PRODUCT_OBSERVATIONS)
	min_qty = random.randint(5, 40)
	# 30% dos produtos terão quantidade baixa
	if random.random() < 0.3:
		quantidade = random.randint(0, min_qty)
	else:
		quantidade = random.randint(min_qty + 1, min_qty + 120)

	return {
		"codigo_barras": random_digits(13),
		"nome_item": f"{nome} {index + 1}",
		"modelo": f"{modelo}-{uuid.uuid4().hex[:4].upper()}",
		"codigo_sku": f"SKU-{uuid.uuid4().hex[:8].upper()}",
		"id_categoria": category_id,
		"id_marca": brand_id,
		"tamanho": random.choice(PRODUCT_SIZES),
		"cor": random.choice(PRODUCT_COLORS),
		"preco": round(random.uniform(15.0, 1200.0), 2),
		"data": (date.today() - timedelta(days=random.randint(0, 365))).isoformat(),
		"quantidade": quantidade,
		"quantidade_minima": min_qty,
		"descricao": f"{descricao} #{index + 1}",
		"observacoes": f"{observacao} #{index + 1}",
	}


def build_client_payload(index: int) -> Dict[str, Any]:
	first = random.choice(CLIENT_FIRST_NAMES)
	last = random.choice(CLIENT_LAST_NAMES)
	full_name = f"{first} {last}"
	cpf = random_digits(11) if random.random() < 0.8 else None
	cnpj = random_digits(14) if random.random() < 0.4 else None
	if not cpf and not cnpj:
		cpf = random_digits(11)

	# Garante unicidade usando uuid curto
	email_local = f"{first.lower()}{last.lower()}{index}{uuid.uuid4().hex[:6]}"
	email = f"{email_local}@exemplo.com"

	# CPF e CNPJ também rotacionados para evitar duplicidade
	cpf = random_digits(9) + str(index).zfill(2)
	cnpj = random_digits(12) + str(index).zfill(2) if cnpj else None
	telefone = random_digits(random.choice([10, 11]))
	endereco = f"{random.choice(STREET_NAMES)} {random.randint(1, 500)}, {random.choice(CITIES)}"

	return {
		"nome": full_name,
		"cpf": cpf,
		"cnpj": cnpj,
		"email": email,
		"endereco": endereco,
		"telefone": telefone,
		"data_nascimento": random_date(),
		"perfil": random.choice(CLIENT_PROFILES),
		"ativo": True,
	}


def seed_products(base_url: str, total: int = PRODUCT_TOTAL) -> None:
	print(f"\n[produtos] Alvo: {total} itens @ {base_url}")
	with httpx.Client(base_url=base_url, timeout=20.0) as client:
		categories = ensure_categories(client)
		brands = ensure_brands(client)

		if not categories:
			print("[produtos] Abortado: nenhuma categoria disponível ou criada.")
			return
		if not brands:
			print("[produtos] Abortado: nenhuma marca disponível ou criada.")
			return

		criados = 0
		falhas = 0

		for idx in range(total):
			payload = build_product_payload(idx, categories, brands)
			try:
				response = client.post(f"{PRODUCT_ENDPOINT}/", json=payload)
				if response.status_code == 200:
					body = response.json()
					if body.get("success"):
						criados += 1
					else:
						falhas += 1
						print(f"[produtos] #{idx + 1} rejeitado: {body.get('message')}")
				else:
					falhas += 1
					print(f"[produtos] #{idx + 1} HTTP {response.status_code}: {response.text}")
			except Exception as exc:
				falhas += 1
				print(f"[produtos] #{idx + 1} exceção: {exc}")

		print(f"[produtos] Finalizado. Criados: {criados}, Falhas: {falhas}\n")


def seed_clients(base_url: str, total: int = CLIENT_TOTAL) -> None:
	print(f"\n[clientes] Alvo: {total} itens @ {base_url}")
	with httpx.Client(base_url=base_url, timeout=20.0) as client:
		criados = 0
		falhas = 0

		for idx in range(total):
			payload = build_client_payload(idx)
			try:
				response = client.post(f"{CLIENT_ENDPOINT}/", json=payload)
				if response.status_code in (200, 201):
					body = response.json()
					if body.get("success"):
						criados += 1
					else:
						falhas += 1
						print(f"[clientes] #{idx + 1} rejeitado: {body.get('message')}")
				else:
					falhas += 1
					print(f"[clientes] #{idx + 1} HTTP {response.status_code}: {response.text}")
			except Exception as exc:
				falhas += 1
				print(f"[clientes] #{idx + 1} exceção: {exc}")

		print(f"[clientes] Finalizado. Criados: {criados}, Falhas: {falhas}\n")


def run_menu() -> None:
	base_url = DEFAULT_BASE_URL
	menu_text = (
		"\n=== Menu de Estresse ===\n"
		"1) Gerar produtos\n"
		"2) Gerar clientes\n"
		"3) Gerar produtos e clientes\n"
		"4) Gerar categorias\n"
		"5) Gerar marcas\n"
		"6) Alterar URL base (atual: {base})\n"
		"0) Sair\n"
	)

	while True:
		print(menu_text.format(base=base_url))
		escolha = input("Selecione uma opção: ").strip()

		if escolha == "1":
			seed_products(base_url)
		elif escolha == "2":
			seed_clients(base_url)
		elif escolha == "3":
			seed_products(base_url)
			seed_clients(base_url)
		elif escolha == "4":
			seed_categories(base_url)
		elif escolha == "5":
			seed_brands(base_url)
		elif escolha == "6":
			nova_url = input("Informe a nova URL base (ex: http://localhost:8000): ").strip().rstrip("/")
			if nova_url:
				base_url = nova_url
				print(f"[menu] URL base atualizada para {base_url}")
			else:
				print("[menu] URL base mantida.")
		elif escolha == "0":
			print("Saindo do menu de estresse.")
			break
		else:
			print("[menu] Opção inválida, tente novamente.")


if __name__ == "__main__":
	run_menu()
