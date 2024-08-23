import socket
import threading
# Bu fonksiyon sunucudan gelen mesajlari surekli olarak dinler ve ekrana yazdirir.
def alinan_mesaj(client_socket):
    while True:
        try:
            # Sunucudan gelen mesaji alir
            mesaj = client_socket.recv(1024).decode('utf-8')
            if not mesaj:
                print("Sunucu ile bağlantı kesildi.")
                break
            else:
                print(mesaj)
        except:
            break

# Bu fonksiyon kullanicinin adini sunucuya gonderir ve onay bekler.
def kullaniciadi_gonderme(client_socket):
    kullanici_adi = input('Kullanıcı adınızı giriniz: ')
    while True:
        # Kullanici adini sunucuya gonderir
        client_socket.send(kullanici_adi.encode('utf-8'))
        # Sunucudan gelen yaniti alir
        yanit = client_socket.recv(1024).decode('utf-8')
        if 'Hosgeldiniz' in yanit:
            print(yanit)
            return kullanici_adi
        else:
            print(yanit)

# Bu fonksiyon kullanicinin yazdigi mesajlari sunucuya gonderir.
def mesaj_gonderme(client_socket, kullanici_adi):
    while True:
        # Kullanicidan mesaj alir
        mesaj = input('Mesajınızı giriniz: ')
        # Mesaji kullanici adı ile birlikte sunucuya gonderir
        client_socket.send(f"{kullanici_adi}: {mesaj}".encode('utf-8'))

# Ana fonksiyon, istemciyi baslatir ve sunucuya baglanır.
def main():
    server_ip = 'localhost'
    tcp_port = 12345

    while True:
        # TCP soketi olusturur
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Sunucuya bağlanır
        client_socket.connect((server_ip, tcp_port))

        # Kullanıci adini sunucuya gonderir ve onay alir
        kullanici_adi = kullaniciadi_gonderme(client_socket)

        if kullanici_adi:
            # Sunucudan gelen mesajlari dinleyen bir thread baslair
            alinan_mesaj_thread = threading.Thread(target=alinan_mesaj, args=(client_socket,))
            alinan_mesaj_thread.daemon = True  # Program kapandiginda thread'leri durdurur
            alinan_mesaj_thread.start()
            # kullanicini mesajlarini sunucuya gonderen fonksiyonu calistirir
            mesaj_gonderme(client_socket, kullanici_adi)

      
        client_socket.close()

if __name__ == '__main__':
    main()
