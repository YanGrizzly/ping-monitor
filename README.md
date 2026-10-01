# Ping Monitor

Aplicação em Python para monitorar conexões de rede de um processo em tempo real.

## Recursos

* Detecção de processo com `psutil`
* Monitoramento de conexões TCP/UDP
* Exibição de IP e porta remotos
* Ping ICMP
* Latência TCP
* Jitter
* Eventos de novas conexões e conexões encerradas
* Interface gráfica com Tkinter
* Estrutura modular dividida em vários arquivos

## Estrutura do projeto

```text
Monitor\\\_Ping\\\_2/
├── main.py
├── gui.py
├── monitor.py
├── latencia.py
├── eventos.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Requisitos

* Windows
* Python 3
* `psutil`

O Tkinter normalmente já acompanha a instalação padrão do Python no Windows.

## Como executar

```powershell
python main.py
```

Na interface, informe o nome do processo que deseja monitorar, por exemplo:

```text
firefox.exe
```

Depois clique em **Iniciar**.

## Observações sobre latência

Nem todo servidor responde a ping ICMP ou aceita conexões TCP genéricas usadas para medição.

Por isso, alguns destinos podem aparecer como:

```text
N/A
```

mesmo quando a conexão do jogo ou aplicativo está ativa normalmente.

## Arquivos

* `main.py` — ponto de entrada do programa
* `gui.py` — interface gráfica
* `monitor.py` — detecção do processo e conexões de rede
* `latencia.py` — ping, latência TCP, jitter e threads
* `eventos.py` — registro de conexões novas e encerradas

## Objetivo do projeto

Este projeto foi criado como exercício prático de Python, redes e monitoramento de processos, com foco em aprendizado e organização modular do código.

## Aviso

O programa apenas consulta informações de processo e rede disponibilizadas pelo sistema operacional. Ele não modifica memória de processos, não injeta código e não altera o tráfego de rede.

