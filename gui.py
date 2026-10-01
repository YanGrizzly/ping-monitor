import tkinter as tk
from tkinter import ttk
import time

from monitor import obter_info_processo

from latencia import (
    iniciar_teste_rede,
    obter_ping,
    obter_jitter,
    obter_tcp,
    limpar_resultados
)

from eventos import (
    verificar_eventos,
    resetar_eventos
)


# =========================
# ESTADO DA GUI
# =========================

monitorando = False

nome_processo_monitorado = ""

inicio_conexoes = {}

after_id = None


# =========================
# INICIAR
# =========================

def iniciar_monitoramento():
    global monitorando
    global nome_processo_monitorado
    global after_id

    if monitorando:
        return


    nome_processo_monitorado = (
        entrada_processo.get()
        .strip()
    )


    if not nome_processo_monitorado:

        status_label.config(
            text="Digite o nome de um processo."
        )

        return


    monitorando = True

    inicio_conexoes.clear()

    resetar_eventos()

    limpar_resultados()


    botao_iniciar.config(
        state="disabled"
    )

    botao_parar.config(
        state="normal"
    )


    status_label.config(
        text=(
            f"Monitorando: "
            f"{nome_processo_monitorado}"
        )
    )


    atualizar_interface()


# =========================
# PARAR
# =========================

def parar_monitoramento():
    global monitorando
    global after_id

    monitorando = False


    if after_id is not None:

        try:
            janela.after_cancel(
                after_id
            )

        except tk.TclError:
            pass

        after_id = None


    botao_iniciar.config(
        state="normal"
    )

    botao_parar.config(
        state="disabled"
    )


    status_label.config(
        text="Monitoramento parado."
    )


    label_nome_processo.config(
        text="Processo: -"
    )

    label_pid.config(
        text="PID: -"
    )

    contador_label.config(
        text="Conexões ativas: 0"
    )


# =========================
# LIMPAR TABELA
# =========================

def limpar_tabela():

    for item in tabela.get_children():

        tabela.delete(item)


# =========================
# ATUALIZAR GUI
# =========================

def atualizar_interface():
    global after_id

    if not monitorando:
        return


    info = obter_info_processo(
        nome_processo_monitorado
    )


    # =========================
    # PROCESSO NÃO ENCONTRADO
    # =========================

    if info is None:

        status_label.config(
            text="Processo não encontrado"
        )

        label_nome_processo.config(
            text="Processo: -"
        )

        label_pid.config(
            text="PID: -"
        )

        contador_label.config(
            text="Conexões ativas: 0"
        )

        limpar_tabela()


        after_id = janela.after(
            2000,
            atualizar_interface
        )

        return


    conexoes = info["conexoes"]


    # =========================
    # INFO DO PROCESSO
    # =========================

    status_label.config(
        text="● Monitorando conexões"
    )

    label_nome_processo.config(
        text=f"Processo: {info['nome']}"
    )

    label_pid.config(
        text=f"PID: {info['pid']}"
    )

    contador_label.config(
        text=(
            f"Conexões ativas: "
            f"{len(conexoes)}"
        )
    )


    # =========================
    # EVENTOS
    # =========================

    novos_eventos = verificar_eventos(
        conexoes
    )


    for evento in novos_eventos:

        texto = (
            f"[{evento['horario']}] "
            f"[{evento['tipo']}] "
            f"{evento['ip']}:"
            f"{evento['porta']} "
            f"| {evento['protocolo']}"
        )

        lista_eventos.insert(
            0,
            texto
        )


    while lista_eventos.size() > 10:

        lista_eventos.delete(
            10,
            tk.END
        )


    # =========================
    # INICIA TESTES
    # =========================

    for conexao in conexoes:

        iniciar_teste_rede(
            conexao["ip"],
            conexao["porta"],
            conexao["protocolo"]
        )


    # =========================
    # TABELA
    # =========================

    limpar_tabela()

    ids_ativos = set()


    for conexao in conexoes:

        ip = conexao["ip"]

        porta = conexao["porta"]

        protocolo = conexao["protocolo"]

        status = conexao["status"]


        conexao_id = (
            ip,
            porta,
            protocolo,
            status
        )


        ids_ativos.add(
            conexao_id
        )


        if (
            conexao_id
            not in inicio_conexoes
        ):

            inicio_conexoes[
                conexao_id
            ] = time.time()


        # =========================
        # TEMPO ATIVO
        # =========================

        tempo_ativo = int(
            time.time()
            - inicio_conexoes[
                conexao_id
            ]
        )


        horas = (
            tempo_ativo // 3600
        )

        minutos = (
            tempo_ativo % 3600
        ) // 60

        segundos = (
            tempo_ativo % 60
        )


        tempo_texto = (
            f"{horas:02}:"
            f"{minutos:02}:"
            f"{segundos:02}"
        )


        # =========================
        # PING
        # =========================

        ping = obter_ping(
            ip
        )


        if ping is None:

            ping_texto = "N/A"

        else:

            ping_texto = (
                f"{ping} ms"
            )


        # =========================
        # TCP
        # =========================

        tcp = obter_tcp(
            ip,
            porta
        )


        if tcp is None:

            tcp_texto = "N/A"

        else:

            tcp_texto = (
                f"{tcp} ms"
            )


        # =========================
        # JITTER
        # =========================

        jitter = obter_jitter(
            ip
        )


        if jitter is None:

            jitter_texto = "N/A"

        else:

            jitter_texto = (
                f"{jitter} ms"
            )


        # =========================
        # INSERE NA TABELA
        # =========================

        tabela.insert(
            "",
            "end",
            values=(
                ip,
                porta,
                protocolo,
                status,
                tempo_texto,
                ping_texto,
                tcp_texto,
                jitter_texto
            )
        )


    # =========================
    # REMOVE CONEXÕES ANTIGAS
    # =========================

    for conexao_id in list(
        inicio_conexoes.keys()
    ):

        if (
            conexao_id
            not in ids_ativos
        ):

            inicio_conexoes.pop(
                conexao_id,
                None
            )


    # =========================
    # PRÓXIMA ATUALIZAÇÃO
    # =========================

    after_id = janela.after(
        2000,
        atualizar_interface
    )


# =========================
# FECHAR JANELA
# =========================

def fechar_app():
    global monitorando

    monitorando = False

    janela.destroy()


# =========================
# CRIAR APP
# =========================

def iniciar_app():

    global janela

    global entrada_processo

    global botao_iniciar
    global botao_parar

    global status_label
    global contador_label

    global label_nome_processo
    global label_pid

    global tabela

    global lista_eventos


    # =========================
    # JANELA
    # =========================

    janela = tk.Tk()

    janela.title(
        "Ping Monitor"
    )

    janela.geometry(
        "1180x650"
    )

    janela.minsize(
        1000,
        550
    )

    janela.protocol(
        "WM_DELETE_WINDOW",
        fechar_app
    )


    # =========================
    # ESTILO
    # =========================

    style = ttk.Style()


    style.configure(
        "Titulo.TLabel",
        font=(
            "Segoe UI",
            20,
            "bold"
        )
    )


    style.configure(
        "Treeview",
        rowheight=28,
        font=(
            "Segoe UI",
            10
        )
    )


    style.configure(
        "Treeview.Heading",
        font=(
            "Segoe UI",
            10,
            "bold"
        )
    )


    # =========================
    # CABEÇALHO
    # =========================

    frame_topo = ttk.Frame(
        janela,
        padding=20
    )

    frame_topo.pack(
        fill="x"
    )


    titulo = ttk.Label(
        frame_topo,
        text="Ping Monitor",
        style="Titulo.TLabel"
    )

    titulo.pack(
        anchor="w"
    )


    subtitulo = ttk.Label(
        frame_topo,
        text=(
            "Monitor de conexões "
            "e latência em tempo real"
        )
    )

    subtitulo.pack(
        anchor="w"
    )


    # =========================
    # CONTROLES
    # =========================

    frame_controle = ttk.LabelFrame(
        janela,
        text="Monitoramento",
        padding=15
    )

    frame_controle.pack(
        fill="x",
        padx=20,
        pady=(0, 10)
    )


    ttk.Label(
        frame_controle,
        text="Processo do jogo:"
    ).pack(
        side="left",
        padx=(0, 8)
    )


    entrada_processo = ttk.Entry(
        frame_controle,
        width=30
    )

    entrada_processo.pack(
        side="left",
        padx=(0, 10)
    )


    botao_iniciar = ttk.Button(
        frame_controle,
        text="Iniciar",
        command=iniciar_monitoramento
    )

    botao_iniciar.pack(
        side="left",
        padx=5
    )


    botao_parar = ttk.Button(
        frame_controle,
        text="Parar",
        command=parar_monitoramento,
        state="disabled"
    )

    botao_parar.pack(
        side="left",
        padx=5
    )


    # =========================
    # STATUS
    # =========================

    frame_status = ttk.Frame(
        janela,
        padding=(20, 5)
    )

    frame_status.pack(
        fill="x"
    )


    status_label = ttk.Label(
        frame_status,
        text="Aguardando..."
    )

    status_label.pack(
        side="left"
    )


    contador_label = ttk.Label(
        frame_status,
        text="Conexões ativas: 0"
    )

    contador_label.pack(
        side="right"
    )


    frame_info = ttk.Frame(
        janela,
        padding=(20, 5)
    )

    frame_info.pack(
        fill="x"
    )


    label_nome_processo = ttk.Label(
        frame_info,
        text="Processo: -"
    )

    label_nome_processo.pack(
        side="left",
        padx=(0, 20)
    )


    label_pid = ttk.Label(
        frame_info,
        text="PID: -"
    )

    label_pid.pack(
        side="left"
    )


    # =========================
    # TABELA
    # =========================

    frame_tabela = ttk.LabelFrame(
        janela,
        text="Conexões Ativas",
        padding=10
    )

    frame_tabela.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )


    colunas = (
        "ip",
        "porta",
        "protocolo",
        "status",
        "tempo",
        "ping",
        "tcp",
        "jitter"
    )


    tabela = ttk.Treeview(
        frame_tabela,
        columns=colunas,
        show="headings"
    )


    cabecalhos = {
        "ip": "IP Remoto",
        "porta": "Porta",
        "protocolo": "Protocolo",
        "status": "Status",
        "tempo": "Tempo Ativo",
        "ping": "Ping ICMP",
        "tcp": "Latência TCP",
        "jitter": "Jitter"
    }


    larguras = {
        "ip": 170,
        "porta": 80,
        "protocolo": 100,
        "status": 120,
        "tempo": 120,
        "ping": 100,
        "tcp": 110,
        "jitter": 90
    }


    for coluna in colunas:

        tabela.heading(
            coluna,
            text=cabecalhos[coluna]
        )

        tabela.column(
            coluna,
            width=larguras[coluna],
            anchor="center"
        )


    scroll = ttk.Scrollbar(
        frame_tabela,
        orient="vertical",
        command=tabela.yview
    )


    tabela.configure(
        yscrollcommand=scroll.set
    )


    scroll.pack(
        side="right",
        fill="y"
    )


    tabela.pack(
        fill="both",
        expand=True
    )


    # =========================
    # EVENTOS
    # =========================

    frame_eventos = ttk.LabelFrame(
        janela,
        text="Eventos Recentes",
        padding=10
    )

    frame_eventos.pack(
        fill="x",
        padx=20,
        pady=(0, 20)
    )


    lista_eventos = tk.Listbox(
        frame_eventos,
        height=6,
        font=(
            "Consolas",
            10
        ),
        borderwidth=0
    )


    lista_eventos.pack(
        fill="x"
    )


    # =========================
    # LOOP
    # =========================

    janela.mainloop()