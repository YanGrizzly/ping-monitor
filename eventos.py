import time


conexoes_anteriores = set()


def gerar_id_conexao(conexao):
    return (
        conexao["ip"],
        conexao["porta"],
        conexao["protocolo"],
        conexao["status"]
    )


def verificar_eventos(conexoes_atuais):
    global conexoes_anteriores

    atuais = set()

    eventos = []


    for conexao in conexoes_atuais:
        conexao_id = gerar_id_conexao(
            conexao
        )

        atuais.add(
            conexao_id
        )


    # =========================
    # NOVAS CONEXÕES
    # =========================

    for conexao_id in atuais:

        if (
            conexao_id
            not in conexoes_anteriores
        ):

            ip, porta, protocolo, status = conexao_id

            horario = time.strftime(
                "%H:%M:%S"
            )

            eventos.append(
                {
                    "tipo": "NOVA",
                    "horario": horario,
                    "ip": ip,
                    "porta": porta,
                    "protocolo": protocolo
                }
            )


    # =========================
    # CONEXÕES ENCERRADAS
    # =========================

    for conexao_id in conexoes_anteriores:

        if (
            conexao_id
            not in atuais
        ):

            ip, porta, protocolo, status = conexao_id

            horario = time.strftime(
                "%H:%M:%S"
            )

            eventos.append(
                {
                    "tipo": "ENCERRADA",
                    "horario": horario,
                    "ip": ip,
                    "porta": porta,
                    "protocolo": protocolo
                }
            )


    conexoes_anteriores = atuais.copy()

    return eventos


def resetar_eventos():
    global conexoes_anteriores

    conexoes_anteriores = set()