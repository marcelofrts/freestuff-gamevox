# 🎮 FreeStuff para GameVox

Um bot automatizado em Python no estilo **FreeStuff** para o **GameVox**, que monitora e notifica promoções de jogos 100% gratuitos (Steam, Epic Games Store, GOG, etc.) diretamente no canal de texto do seu servidor.

---

## 🏆 Melhor Opção: Hospedar 100% Grátis com GitHub Actions (Sem Servidor Próprio)

Esta é a opção **mais recomendada** porque:
* **Nunca será cobrado**: É 100% gratuito para sempre (não pede cartão de crédito).
* **Nunca cai por inatividade**: O GitHub executa a verificação a cada 30 minutos automaticamente em seus próprios servidores.
* **Seguro**: Sua URL do Webhook do GameVox fica guardada em segredo criptografado.

### Como configurar em 5 minutos:

1. **Crie um repositório no seu GitHub**:
   * Acesse [github.com/new](https://github.com/new).
   * Dê o nome que quiser (ex: `freestuff-gamevox`) e escolha se quer **Público** ou **Privado**.
   * Suba todos os arquivos deste projeto para lá.

2. **Adicionar o link do Webhook nos Secrets do GitHub**:
   * No seu repositório no GitHub, clique em **Settings** (Configurações).
   * No menu lateral esquerdo, vá em **Secrets and variables** -> **Actions**.
   * Clique no botão verde **New repository secret**.
   * No campo **Name**, digite exatamente:
     ```
     GAMEVOX_WEBHOOK_URL
     ```
   * No campo **Secret**, cole a URL do seu Webhook do GameVox (obtida no canal de texto do GameVox).
   * Clique em **Add secret**.

3. **Pronto! 🎉**:
   * O GitHub Actions irá rodar a cada 30 minutos sozinho.
   * Se quiser disparar um teste imediatamente, vá na aba **Actions** no topo do seu repositório, clique em **Monitorar Jogos Grátis (GameVox)** e depois em **Run workflow**!

---

## ⚙️ Outras Opções de Hospedagem

Se você já possuir uma máquina própria (VPS) ou preferir rodar com Docker:

* **Docker**: execute `docker compose up -d`
* **Linux (systemd)**: utilize o arquivo `freestuff-gamevox.service`
* **Localmente**: execute `python main.py`

---

## ⚙️ Personalização no arquivo `.env` (ou no workflow)

| Variável | Padrão | Descrição |
| :--- | :--- | :--- |
| `GAMEVOX_WEBHOOK_URL` | *(vazio)* | A URL do webhook do seu canal no GameVox |
| `CHECK_INTERVAL_MINUTES` | `15` | Tempo de espera (em minutos) entre cada checagem |
| `PLATFORM_FILTER` | `pc` | Plataformas desejadas (`pc`, `steam`, `epic-games-store`, `gog`, `all`) |
| `TYPE_FILTER` | `game` | Tipo de brinde (`game` para jogos completos, `loot` para itens/DLCs, `all`) |
| `NOTIFY_ROLE` | *(vazio)* | Menção de cargo opcional (ex: `@everyone` ou `@here`) |
