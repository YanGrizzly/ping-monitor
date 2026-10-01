import psutil
import socket


def buscar_processo(nome_processo):
    nome_processo = nome_processo.lower().strip()

    for processo in psutil.process_iter(["pid", "name"]):
        try:
            nome = processo.info.get("name")

            if nome and nome_processo in nome.lower():
                return processo

        except (
            psutil.AccessDenied,
            psutil.NoSuchProcess
        ):
            continue

    return None


def obter_conexoes(processo):
    conexoes_encontradas = []

    try:
        conexoes = processo.net_connections(
            kind="inet"
        )

    except (
        psutil.AccessDenied,
        psutil.NoSuchProcess
    ):
        return conexoes_encontradas


    for conexao in conexoes or []:

        if not conexao.raddr:
            continue

        if conexao.raddr.ip == "127.0.0.1":
            continue

        if (
            conexao.status
            != psutil.CONN_ESTABLISHED
        ):
            continue


        if (
            conexao.type
            == socket.SOCK_STREAM
        ):
            protocolo = "TCP"

        elif (
            conexao.type
            == socket.SOCK_DGRAM
        ):
            protocolo = "UDP"

        else:
            protocolo = "Desconhecido"


        conexoes_encontradas.append({
            "ip": conexao.raddr.ip,
            "porta": conexao.raddr.port,
            "protocolo": protocolo,
            "status": conexao.status
        })


    return conexoes_encontradas


def obter_info_processo(nome_processo):
    processo = buscar_processo(
        nome_processo
    )

    if processo is None:
        return None


    return {
        "pid": processo.pid,
        "nome": processo.name(),
        "conexoes": obter_conexoes(
            processo
        )
    }