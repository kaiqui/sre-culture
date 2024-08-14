# Canary Deploy e Observalibilidaed: SRE Culture

## Integração do ArgoCD com Minikube

O ArgoCD é uma ferramenta de GitOps que facilita a gestão de aplicações Kubernetes, enquanto o Minikube cria clusters Kubernetes locais para desenvolvimento e teste. A seguir, estão os passos para integrar o ArgoCD com um cluster Minikube.

### Passos para Integrar ArgoCD com Minikube

1. **Instalar o Minikube**: Certifique-se de ter o Minikube instalado e funcionando. Consulte a [documentação oficial do Minikube](https://minikube.sigs.k8s.io/docs/start/) para instruções detalhadas.

2. **Iniciar o Minikube**:
   ```bash
   minikube start
   ```

3. **Instalar o kubectl**: Garanta que o `kubectl` esteja instalado e configurado para se conectar ao seu cluster Minikube.

4. **Instalar o ArgoCD**:

   - Crie um namespace para o ArgoCD:
     ```bash
     kubectl create namespace argocd
     ```

   - Aplique o manifesto do ArgoCD:
     ```bash
     kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
     ```

5. **Verificar o Funcionamento do ArgoCD**:
   ```bash
   kubectl get pods -n argocd
   ```

6. **Acessar a Interface Web do ArgoCD**:

   - Use o serviço `NodePort` para acessar o ArgoCD no Minikube. Descubra o NodePort:
     ```bash
     kubectl get svc -n argocd
     ```

   - Redirecione a porta para o localhost:
     ```bash
     kubectl port-forward svc/argocd-server -n argocd 8080:80 &
     ```

   - Acesse a interface web do ArgoCD em `http://localhost:8080`.

7. **Obter as Credenciais de Login**:

   - O nome de usuário padrão é `admin`. Para obter a senha, execute:
     ```bash
     echo $(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 --decode)
     ```

8. **Fazer Login na Interface Web**:

   - Use o nome de usuário `admin` e a senha obtida no passo anterior para fazer login.

9. **Configurar ArgoCD**:

   - Após o login, você pode adicionar repositórios Git, configurar aplicativos e gerenciar o ciclo de vida de suas aplicações Kubernetes diretamente da interface web do ArgoCD.

## Configuração Básica de Observabilidade

A seguir estão os passos detalhados para instalar o Helm, integrá-lo com o Kubernetes e configurar o Prometheus para coleta de métricas:

### 1. **Instalar o Helm**

Helm é um gerenciador de pacotes para Kubernetes que facilita a instalação e gerenciamento de aplicativos.

#### 1.1 Instalação do Helm no Linux/macOS:

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### 2. **Verificar a Instalação do Helm**

Para confirmar que o Helm foi instalado corretamente, execute:

```bash
helm version
```

### 3. **Adicionar o Repositório do Helm**

Antes de instalar qualquer pacote, adicione o repositório oficial do Helm:

```bash
helm repo add stable https://charts.helm.sh/stable
helm repo update
```

### 4. **Instalar o Prometheus com Helm**

Agora que o Helm está instalado, use-o para instalar o Prometheus no Kubernetes.

#### 4.1 Criar um Namespace para Prometheus

Crie um namespace dedicado para Prometheus:

```bash
kubectl create namespace monitoring
```

#### 4.2 Adicionar e Instalar o Prometheus

Adicione o repositório do Prometheus, faça isso agora:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

Instale o Prometheus usando o Helm:

```bash
helm install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --set server.global.scrape_interval="15s" \
  --set server.persistentVolume.enabled=false
```

### 5. **Verificar a Configuração**

Verifique se os pods do Prometheus estão em execução:

```bash
kubectl get pods -n monitoring
```

### 6. **Adicionar e Instalar Grafana para Visualização**

Grafana é uma ferramenta popular para visualizar métricas coletadas por Prometheus e outros plugins.

#### 6.1 Instalar o Grafana com Helm

Adicione o repositório Helm do Grafana e instale-o:

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm install grafana grafana/grafana --namespace monitoring
```

#### 6.2 Acessar o Grafana

1. Verifique o nome do pod do Grafana:

   ```bash
   kubectl get pods -n monitoring -l app.kubernetes.io/name=grafana
   ```

2. Crie um `port-forward` para acessar o Grafana localmente:

   ```bash
   kubectl port-forward -n monitoring svc/grafana 3000:80 &
   ```

3. Abra seu navegador e acesse `http://localhost:3000`.

4. Use o usuário e senha padrão para login:
   - **Usuário**: `admin`
   - **Senha**: `kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo`

#### 6.3 Adicionar Prometheus como Fonte de Dados no Grafana

1. No Grafana, vá para **Configuration > Data Sources**.
2. Clique em **Add data source**.
3. Escolha **Prometheus**.
4. Configure a URL como `http://prometheus-server.monitoring.svc.cluster.local:80`.
5. Clique em **Save & Test** para verificar a conexão.

### 7. **Deploy da Aplicação no ArgoCD**

### Passo 1: Acessar o ArgoCD
1. **Abra o navegador** e acesse a interface web do ArgoCD. Geralmente, ela estará disponível no endereço fornecido pelo seu administrador, como `http://<argocd-url>`.

2. **Faça login** com suas credenciais. Se você não sabe o usuário e senha, entre em contato com o administrador ou utilize os comandos para obter as credenciais (ex: via `kubectl`).

### Passo 2: Criar um Novo Aplicativo
1. **No painel principal do ArgoCD**, clique em "New App" para criar um novo aplicativo.

### Passo 3: Configurar o Aplicativo
1. **Preencha os detalhes do aplicativo**:
    - **Application Name**: Escolha um nome para o seu aplicativo, por exemplo, `fastapi-app`.
    - **Project**: Selecione o projeto no qual o aplicativo será criado (geralmente `default` se você não tiver projetos específicos).
    - **Sync Policy**: Deixe como `Manual` se quiser controlar os deploys ou `Automatic` para que o ArgoCD sincronize automaticamente.

2. **Configurar a origem do código**:
    - **Repository URL**: Insira a URL do repositório Git onde seu código e os manifests YAML estão armazenados.
    - **Revision**: Especifique o branch ou tag que você deseja implantar (por exemplo, `main`).
    - **Path**: Insira o caminho dentro do repositório onde os manifests estão localizados (por exemplo, `/k8s` se os arquivos estão em uma pasta `k8s`).

3. **Definir o cluster e o namespace**:
    - **Cluster URL**: Deixe o valor padrão para o cluster atual ou selecione o cluster onde deseja implantar.
    - **Namespace**: Especifique o namespace Kubernetes onde o aplicativo será implantado (ex: `default`).

4. **Configurar as opções de sincronização**:
    - **Directory Recurse**: Marque essa opção se o path contém subdiretórios que devem ser incluídos.
    - **Prune Resources**: Ative essa opção se você deseja que o ArgoCD remova os recursos que foram deletados do repositório Git.
  
5. **Configurar opções de parâmetros (opcional)**:
    - Você pode adicionar `Helm Values` ou parâmetros específicos de configuração aqui, se estiver usando um repositório Helm.

### Passo 4: Revisar e Criar o Aplicativo
1. **Revise as configurações** para garantir que todos os parâmetros estejam corretos.

2. **Clique em "Create"** para criar o aplicativo. Isso o levará para a página de detalhes do aplicativo.

### Passo 5: Sincronizar o Aplicativo
1. **Na página de detalhes do aplicativo**, você verá o estado do aplicativo e os recursos que ele contém.

2. **Clique em "Sync"** para sincronizar o estado do cluster com o repositório Git. Isso iniciará o processo de deploy.

3. **Acompanhe o progresso** na interface. Você verá o status dos pods, serviços e outros recursos sendo criados.

### Passo 6: Verificar o Deploy
1. **Após a sincronização**, verifique o status dos recursos para garantir que tudo foi implantado corretamente.
    - Verde significa que o recurso está sincronizado e saudável.
    - Vermelho ou amarelo pode indicar um problema que precisa ser investigado.

2. **Teste a aplicação** acessando o serviço exposto (se aplicável) para garantir que ela esteja funcionando como esperado.


### 8. **Criar Dashboards para Monitorar os Four Golden Signals da Aplicação deste Repositório**

Agora que o Grafana está conectado ao Prometheus, você pode criar dashboards para monitorar os "Four Golden Signals":

1. **Latência**:
   - Query: `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{job="fastapi-metrics"}[5m])) by (le))`
2. **Tráfego**:
   - Query: `sum(rate(http_requests_total{job="fastapi-metrics"}[5m])) by (job)`
3. **Erros**:
   - Query: `sum by(job) (rate(http_requests_errors_total {job="fastapi-metrics"}[5m]))`
4. **Saturação**:
   - Query: `sum(rate(container_cpu_usage_seconds_total{namespace="default"}[5m])) by (pod)`

---

## Canary Deployment com ArgoCD

### 1. **Instalar o Argo Rollouts**

Primeiro, instale o Argo Rollouts no seu cluster Kubernetes:

```bash
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml
```

### 2. **Configurar o Argo Rollouts no ArgoCD**

Adicione a extensão do Argo Rollouts ao ArgoCD para que ele possa reconhecer e gerenciar recursos do tipo `Rollout`.

### 3. **Modificar seus Manifests Kubernetes**

Substitua o recurso `Deployment` por `Rollout`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app-rollout
  namespace: default
spec:
  replicas: 10
  revisionHistoryLimit: 2
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app-container
        image: my-app-image:stable
        ports:
        - containerPort: 80
  strategy:
    canary:
      canaryService: my-app-canary
      stableService: my-app-stable
      steps:
      - setWeight: 10
      - pause: {duration: 1m}
      - setWeight: 30
      - pause: {duration: 1m}
      - setWeight: 50
      - pause: {duration: 1m}
      - setWeight: 100
```

### 4. **Configurar os Serviços do Kubernetes**

Defina dois serviços: um para o tráfego canário e outro para o tráfego estável.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-stable
  namespace: default
spec:
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 80

apiVersion: v1
kind: Service
metadata:
  name: my

-app-canary
  namespace: default
spec:
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 80
```

### 5. **Criar o Aplicativo no ArgoCD**

Siga os passos para criar o aplicativo no ArgoCD, apontando para o repositório Git onde você configurou seus manifests YAML que contêm os recursos `Rollout`.

### 6. **Sincronizar e Monitorar o Deploy**

Inicie a sincronização do aplicativo através da interface do ArgoCD ou CLI, e monitore o progresso do rollout:

```bash
kubectl argo rollouts get rollout my-app-rollout -n default
```

### 7. **Reverter se Necessário**

Se o rollout falhar ou houver problemas, use ArgoCD e Argo Rollouts para reverter rapidamente para a versão anterior.

---

## Benefícios do Canary Deployment com ArgoCD e Argo Rollouts

- **Incremental Traffic Shift**: Minimize riscos redirecionando o tráfego para a nova versão de forma incremental.
- **Automated Rollbacks**: Garanta estabilidade com rollbacks automáticos em caso de falhas.
- **Observabilidade**: Acompanhe o progresso do deployment e identifique problemas precocemente.
- **Compatibilidade com ArgoCD**: Gerencie o ciclo de vida das suas aplicações de maneira GitOps.

---