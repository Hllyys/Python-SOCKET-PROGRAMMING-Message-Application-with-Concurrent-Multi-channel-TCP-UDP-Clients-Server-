import socket
import threading
import multiprocessing

clients = {}
client_lock = threading.Lock()

def broadcast_message(message, sender_username=None, protocol=None, udp_socket=None):
    # clients sozlugune erisim sirasinda veri tutarliligini saglsmsk icin kilit kullaniliyor.
    with client_lock:
        # clients sozlugundeki kullanicilari dolas
        for username, client_info in clients.items():
            # Mesaji gonderen kullaniciya mesaj gondermemek icin kontrol yap
            if sender_username and username == sender_username:
                continue
            if client_info.get('protocol') == 'TCP':
                client_socket = client_info['socket']
                # Eğer TCP soketi mevcutsa, mesaji bu kullanıiciya gonder
                if client_socket:
                    client_socket.send(message.encode('utf-8'))
            elif client_info.get('protocol') == 'UDP':
                # UDP soketi mevcutsa ve udp_socket parametresi verilmisse, mesajı kullaniciya gonder
                if udp_socket:
                    udp_socket.sendto(message.encode('utf-8'), client_info['address'])

def remove_client(username):
    with client_lock:
        # Verilen kullanici adi clients sozlugunde var mi diye kontrol edilir.
        if username in clients:
            # eger kullanici clients sozlugunde varsa, kullanici bu odadan ayrilmistir kullanici clients sözlüğünden silinir.
            del clients[username]
            print(f'{username} odadan ayrıldı.')


def handle_tcp_client(client_socket, address):
    def handle_username(client_socket):
        # kullanici adinin alinmasi ixin bir ic ice fonksiyon tanımlanır.
        while True:
            # Kullanıcı adı verisinin alinmasi
            username_data = client_socket.recv(1024)
            # Eğer veri alinmamissa, bağlantı sonlandirilir ve fonksiyon None döner.
            if not username_data:
                return None
            username = username_data.decode('utf-8').strip()
            with client_lock:
                # Eğer kullanıcı adı zaten mevcutsa, istemciye bir hata mesajı gönderilir.
                if username in clients:
                    client_socket.send(b'Bu kullanici adi zaten alinmis, lutfen baska bir kullanici adi girin.')
                else:
                    # Eğer kullanıcı adı mevcut değilse, kullanıcı adı geçerli kabul edilir ve fonksiyon kullanıcı adını döner.
                    return username

    username = None
    while True:
        # Kullanıcı adının alınması
        username = handle_username(client_socket)
        # eger kulanici adi alındıysa, donguden cikilir.
        if username:
            break

    welcome_message = f'Hosgeldiniz {username} [TCP] ile baglisiniz'
    print(welcome_message)
    with client_lock:
        # Yeni kullanici clients sozlugune eklenir.
        clients[username] = {'socket': client_socket, 'address': address, 'protocol': 'TCP'}
    # Tüm kullanicilara hoşgeldin mesajı gönderilir.
    broadcast_message(welcome_message)
    # Yeni kullanıcıya hoşgeldin mesajı gönderilir.
    client_socket.send(f'Hosgeldiniz {username} [TCP] ile baglisiniz'.encode('utf-8'))
    
    # Kullanıcıya gelen mesajların alinmasi ve yayinlanmasi için döngü
    while True:
        try:
            # İstemciden mesaj alınır
            message = client_socket.recv(1024)
            # Eğer hiç veri alınmamışsa, bağlantı sonlandırılır ve döngüden çıkılır.
            if not message:
                break
            # Gelen mesaj formatlanır (kullanıcı adı eklenir)
            formatted_message = f'{username}[TCP]: {message.decode("utf-8")}'
            print(formatted_message)
            # Tüm kullanıcılara formatlanmış mesaj gönderilir.
            broadcast_message(formatted_message, sender_username=username)
        except:
            # Eger bir hata olusursa, döngüden cikilir.
            break

    # Eğer kullanıcı adı varsa, kullanıcıdan ayrıldığına dair mesaj konsola yazdırılır.
    if username:
        print(f'{username} [TCP] sohbet odasindan ayrildi.')
        # Kullanıcı odadan ayrıldığı için clients sözlüğünden silinir.
        remove_client(username)
        # Tüm kullanıcılara kullanıcının odadan ayrıldığına dair mesaj gönderilir.
        broadcast_message(f'{username} [TCP] sohbet odasindan ayrildi.')
        # İstemci soketi kapatılır.
        client_socket.close()


def tcp_server():
    # TCP sunucusunun başlatılması
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bağlantıyı tekrar kullanmak için soket seçenekleri ayarlanır.
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # TCP sunucusu, localhost ve 12345 portunda dinlemeye başlar.
    tcp_socket.bind(('localhost', 12345))
    # Sunucu, 5 bağlantıyı dinlemek üzere hazır hale gelir.
    tcp_socket.listen(5)
    print('TCP sunucusu başlatıldı ve bağlantılar dinleniyor...')

    while True:
        # Yeni bir istemci bağlantısı kabul edilir.
        client_socket, address = tcp_socket.accept()
        # Bağlantı kabul edildiğinde istemci adresi konsola yazdırılır.
        print(f'{address} adresinden yeni bir TCP bağlantısı kabul edildi.')
        # Yeni bir iş parçacığı oluşturularak bu istemci için işlemler yapılır.
        threading.Thread(target=handle_tcp_client, args=(client_socket, address)).start()


def handle_udp_client(udp_socket, address, initial_message):
    def handle_username(udp_socket, address, initial_message):
        # İlk gelen mesajdan kullanıcı adının alınması için bir iç içe fonksiyon tanımlanır.
        username = initial_message.decode('utf-8').strip()
        with client_lock:
            # Eger kullanici adi zaten mevcutsa
            if username in clients:
                udp_socket.sendto(b'Bu kullanici adi zaten alinmis, lutfen baska bir kullanici adi girin.', address)
                return None
            else:
                # Eğer kullanici adı mevcut degilse
                udp_socket.sendto(f'Hosgeldiniz {username} UDP ile baglisiniz'.encode('utf-8'), address)
                return username

    # kullanici adinin alinmasi
    username = handle_username(udp_socket, address, initial_message)
    if username:
        # Yeni kullanıcı clients sözlüğüne eklenir.
        with client_lock:
            clients[username] = {'address': address, 'protocol': 'UDP'}
        # Yeni kullanıcıya hoşgeldin mesajı gönderilir.
        welcome_message = f'Hosgeldiniz {username} [UDP] ile baglisiniz'
        print(welcome_message)
        # Tüm kullanıcılara yeni kullanıcının bağlandığına dair mesaj gönderilir.
        broadcast_message(welcome_message)
    

    udp_socket.sendto('Mesajınızı giriniz: '.encode('utf-8'), address)
    
    # Kullanıcının mesajlarını alması ve yayması için döngü
    while True:
        try:
            # İstemciden mesaj alınır
            message, _ = udp_socket.recvfrom(1024)
            if not message:
                break
            message_str = message.decode("utf-8")
            if "sohbet odasindan ayrildi" in message_str:
                print(message_str)
                #kullanicilara ayrilma mesaji gönderilir
                broadcast_message(message_str)
                # Kullanici clients sozlugunden silinir
                remove_client(username)
                break
            # Formatlanmış mesaj oluşturulur
            formatted_message = f'{username}[UDP]: {message_str}'
            print(formatted_message)
            # Tüm kullanıcılara formatlanmış mesaj gönderilir
            broadcast_message(formatted_message, sender_username=username, protocol='UDP', udp_socket=udp_socket)
        except:
            break

    # mesaj konsola yazdirma
    if username:
        print(f'{username} [UDP] sohbet odasindan ayrildi.')
        # Kullanıcı clients sözlüğünden silinir
        remove_client(username)
        # Tüm kullanıcılara ayrılma mesajı gönderilir
        broadcast_message(f'{username} [UDP] sohbet odasindan ayrildi.')


def udp_server():
    # UDP sunucusunun başlatılması
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bağlantıyı tekrar kullanmak için soket seçenekleri ayarlanır.
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # UDP sunucusu, localhost ve 12346 portunda dinlemeye başlar.
    udp_socket.bind(('localhost', 12346))
    print('UDP sunucusu başlatıldı ve mesajlar dinleniyor...')

    while True:
        # Yeni bir mesaj alındığında, istemci adresi ile birlikte işlenir.
        message, address = udp_socket.recvfrom(1024)
        # Bağlantı kabul edildiğinde istemci adresi konsola yazdirilir.
        print(f'{address} adresinden gelen UDP bağlantısı kabul edildi.')
        # Gelen mesajı işlemek için handle_udp_client fonksiyonu cagrilir.
        handle_udp_client(udp_socket, address, message)


if __name__ == '__main__':
    tcp_process = multiprocessing.Process(target=tcp_server)
    udp_process = multiprocessing.Process(target=udp_server)

    tcp_process.start()
    udp_process.start()

    tcp_process.join()
    udp_process.join()
