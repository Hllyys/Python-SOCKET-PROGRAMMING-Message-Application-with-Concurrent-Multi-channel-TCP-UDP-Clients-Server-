import socket
import threading
# Bu fonksiyon sunucudan gelen mesajlari surekli olarak dinler ve ekrana yazdirir.
def alinan_mesaj(udp_socket):
    while True:
        try:
            # Sunucudan gelen mesaji alir
            mesaj, _ = udp_socket.recvfrom(1024)
            if not mesaj:
                print("Sunucu ile bağlantı kesildi.")
                break
            else:
                mesaj_str = mesaj.decode('utf-8')
                if mesaj_str.strip():
                    print(mesaj_str)
        except:
            break

# Bu fonksiyon kullanicinin adini sunucuya gonderir ve onay bekler.
def kullaniciadi_gonderme(udp_socket, server_address):
    kullanici_adi = input('Kullanıcı adınızı giriniz: ')
    while True:
        # Kullanici adini sunucuya gonderir
        udp_socket.sendto(kullanici_adi.encode('utf-8'), server_address)
        # Sunucudan gelen yaniti alir
        yanit, _ = udp_socket.recvfrom(1024)
        yanit_str = yanit.decode('utf-8')
        print(yanit_str)
        if "Hosgeldiniz" in yanit_str:
            return kullanici_adi

# Bu fonksiyon kullanicinin yazdigi mesajlari sunucuya gonderir.
def mesaj_gonderme(udp_socket, kullanici_adi, server_address):
    while True:
        try:
            mesaj = input()
            if mesaj.lower() == 'exit':  # kullanici cikis yapmak isterse
                udp_socket.sendto(f"{kullanici_adi} sohbet odasindan ayrildi.".encode('utf-8'), server_address)
                break
            else:
                mesaj = f'{kullanici_adi}: {mesaj}'
                udp_socket.sendto(mesaj.encode('utf-8'), server_address)
        except Exception as e:
            print("Hata:", e)
            break

# Ana fonksiyon, istemciyi baslatir ve sunucuya baglanir.
def main():
    server_ip = 'localhost'
    udp_port = 12346
    server_address = (server_ip, udp_port)

    # UDP soketi olusturur
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # kullanici adini sunucuya gonderir ve onay alir
    kullanici_adi = kullaniciadi_gonderme(udp_socket, server_address)
    
    if kullanici_adi:
        # Sunucudan gelen mesajlarii dinleyen bir thread baslatir
        alinan_mesaj_thread = threading.Thread(target=alinan_mesaj, args=(udp_socket,))
        alinan_mesaj_thread.daemon = True  # Program kapandiğinda thread'leri durdurur
        alinan_mesaj_thread.start()
        # kullanicinin mesajlarini sunucuya gonderen fonksiyonu calıstırır
        mesaj_gonderme(udp_socket, kullanici_adi, server_address)

 
    udp_socket.close()

if __name__ == '__main__':
    main()
