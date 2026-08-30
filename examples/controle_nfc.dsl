dispositivo controle {

    inteiro tentativas = 3;

    ao botao(1) {

        # lê um cartão NFC
        cartao = nfc.ler();

        se cartao.valido == verdadeiro {
            led.verde();
            esperar(1500);
        }
        senao {
            led.vermelho();
        }
    }
}
