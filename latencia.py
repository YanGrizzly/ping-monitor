import subprocess
import socket
import time
import re
import threading


ultimo_ping = {}

resultados_ping = {}
resultados_tcp = {}
jitter_ping = {}

testes_em_andamento = set()

lock = threading.Lock()


def medir_ping(ip):
    try:
        resultado = subprocess.run(
            [
                "ping",
                "-n", "1",
                "-w", "800",
                ip
            ],
            capture_output=True,
            text=True,
            encoding="cp850",
            errors="ignore",
            timeout=2,
            creationflags=getattr(
                subprocess,
                "CREATE_NO_WINDOW",
                0
            )
        )

        match = re.search(
            r"(?:tempo|time)[=<]\s*(\d+)\s*ms",
            resultado.stdout,
            re.IGNORECASE
        )

        if match:
            return int(match.group(1))

    except (
        subprocess.TimeoutExpired,
        OSError
    ):
        pass

    return None


def medir_tcp(ip, porta):
    inicio = time.perf_counter()

    try:
        conexao = socket.create_connection(
            (ip, porta),
            timeout=0.8
        )

        fim = time.perf_counter()

        conexao.close()

        return round(
            (fim - inicio) * 1000
        )

    except (
        socket.timeout,
        ConnectionRefusedError,
        OSError
    ):
        return None


def atualizar_metricas(
    ip,
    porta,
    protocolo
):
    chave = (
        ip,
        porta,
        protocolo
    )

    try:
        # =========================
        # PING ICMP
        # =========================

        ping_atual = medir_ping(ip)

        with lock:

            if ping_atual is not None:

                anterior = ultimo_ping.get(ip)

                if anterior is None:
                    jitter = 0

                else:
                    jitter = abs(
                        ping_atual - anterior
                    )

                ultimo_ping[ip] = ping_atual
                resultados_ping[ip] = ping_atual
                jitter_ping[ip] = jitter

            else:
                resultados_ping[ip] = None
                jitter_ping[ip] = None


        # =========================
        # LATÊNCIA TCP
        # =========================

        if protocolo == "TCP":

            tcp = medir_tcp(
                ip,
                porta
            )

        else:
            tcp = None


        with lock:
            resultados_tcp[
                (ip, porta)
            ] = tcp

    finally:

        with lock:
            testes_em_andamento.discard(
                chave
            )


def iniciar_teste_rede(
    ip,
    porta,
    protocolo
):
    chave = (
        ip,
        porta,
        protocolo
    )

    with lock:

        if chave in testes_em_andamento:
            return

        testes_em_andamento.add(
            chave
        )


    thread = threading.Thread(
        target=atualizar_metricas,
        args=(
            ip,
            porta,
            protocolo
        ),
        daemon=True
    )

    thread.start()


def obter_ping(ip):
    with lock:
        return resultados_ping.get(ip)


def obter_jitter(ip):
    with lock:
        return jitter_ping.get(ip)


def obter_tcp(ip, porta):
    with lock:
        return resultados_tcp.get(
            (ip, porta)
        )


def limpar_resultados():
    with lock:

        ultimo_ping.clear()
        resultados_ping.clear()
        resultados_tcp.clear()
        jitter_ping.clear()
        testes_em_andamento.clear()