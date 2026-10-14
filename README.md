# 🎵 Playcatch

API de streaming de música: músicas, playlists, containers, Kubernetes, Istio e CI/CD.

```
Cliente → Istio Ingress Gateway → [mTLS] → Playcatch API (FastAPI, 2 réplicas) → [mTLS] → PostgreSQL
```

## Pré-requisitos
Python 3.12+, Docker, Minikube, kubectl, Helm, istioctl, Terraform (opcional).

## Etapa 1 — API local
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
uvicorn app.main:app --reload      # SQLite por padrão
```
Swagger: http://localhost:8000/docs

| Método | Rota | Descrição |
|---|---|---|
| POST/GET | `/songs` | cria / lista (filtros `artist`, `genre`, paginação) |
| GET/PUT/DELETE | `/songs/{id}` | detalhe / atualiza / remove |
| POST/GET | `/playlists` | cria / lista |
| GET/PUT/DELETE | `/playlists/{id}` | detalhe / atualiza / remove |
| POST/DELETE | `/playlists/{id}/songs/{song_id}` | adiciona / remove música |
| GET | `/health` | liveness/readiness |

## Etapa 2 — Docker
```bash
docker compose up --build
curl localhost:8000/health
docker compose logs -f api
```

## Etapa 3 — Kubernetes + Helm (Minikube)
```bash
minikube start --cpus=4 --memory=6g
eval $(minikube docker-env)              # build direto no Docker do Minikube
docker build -t playcatch-api:latest .
helm install playcatch helm/playcatch -n playcatch --create-namespace
kubectl get pods -n playcatch
kubectl port-forward svc/playcatch 8000:80 -n playcatch
```

## Etapa 4 — Istio, CI/CD e Terraform
```bash
istioctl install --set profile=demo -y
kubectl label namespace playcatch istio-injection=enabled --overwrite
kubectl rollout restart deploy/playcatch -n playcatch
kubectl rollout restart statefulset/playcatch-postgres -n playcatch
kubectl apply -f istio/
minikube tunnel                           # em outro terminal
curl http://$(kubectl get svc istio-ingressgateway -n istio-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}')/health
```
Teste da segurança: um pod sem sidecar (ou outro namespace) chamando `playcatch` deve ser recusado.

**Terraform** (namespace + release Helm):
```bash
cd terraform && cp terraform.tfvars.example terraform.tfvars
terraform init && terraform apply
```
**GitHub Actions** (`.github/workflows/ci-cd.yml`): testes → lint Helm/validate Terraform → build/push no GHCR → `helm upgrade`. Configure o secret `KUBE_CONFIG` (base64) para o job de deploy.

## Decisões técnicas
- SQLAlchemy 2.0 com SQLite no dev e PostgreSQL em container/cluster (`DATABASE_URL`).
- Relação N:N playlist↔música via tabela associativa.
- Imagem não-root; credenciais via Secret (em produção, use um gerenciador de segredos).
- Istio: mTLS STRICT + `deny-all` + allow explícito, retries/timeouts e outlier detection.
