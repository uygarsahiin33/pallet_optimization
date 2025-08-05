# Yeniden ortam başlatıldığı için kodu sıfırdan başlatıyoruz
# 1. Gerekli kütüphaneler ve temel değişkenler

import plotly.graph_objects as go

tasima_birimi = ""
tasima_birimleri = {
    "palet": {"genislik": 120, "derinlik": 100, "yukseklik": 180, "max_agirlik": 1000},
    "rulot": {"genislik": 100, "derinlik": 100, "yukseklik": 216, "max_agirlik": 1000}
}

product_catalog = {
    "1": {"id": "A", "genislik": 60, "derinlik": 40, "yukseklik": 30, "agirlik": 50},
    "2": {"id": "B", "genislik": 60, "derinlik": 40, "yukseklik": 60, "agirlik": 50},
    "3": {"id": "C", "genislik": 40, "derinlik": 30, "yukseklik": 20, "agirlik": 30},
    "4": {"id": "D", "genislik": 30, "derinlik": 20, "yukseklik": 25, "agirlik": 10},
    "5": {"id": "E", "genislik": 50, "derinlik": 50, "yukseklik": 50, "agirlik": 70},
    "6": {"id": "F", "genislik": 20, "derinlik": 20, "yukseklik": 20, "agirlik": 5},
    "7": {"id": "G", "genislik": 30, "derinlik": 60, "yukseklik": 20, "agirlik": 40},
}

yerlesen_urunler = []
toplam_agirlik = 0
katman_y = 0

# Palet bilgilerini seçelim (örnek olarak palet seçiyoruz burada)
tasima_birimi = "palet"
GENISLIK = tasima_birimleri[tasima_birimi]["genislik"]
DERINLIK = tasima_birimleri[tasima_birimi]["derinlik"]
YUKSEKLIK = tasima_birimleri[tasima_birimi]["yukseklik"]
MAX_AGIRLIK = tasima_birimleri[tasima_birimi]["max_agirlik"]
bosluklar = [(0, 0, GENISLIK, DERINLIK)]

# Devamında yardımcı fonksiyonlar tanımlanacak...

# Devam: hacim doluluk oranı, destek kontrolü, çakışma kontrolü, yerleştirilen ürün görselleştirme


def hacim_doluluk_orani():
    dolu_hacim = sum(u["genislik"] * u["derinlik"] * u["yukseklik"] for u in yerlesen_urunler)
    oran = (dolu_hacim / (GENISLIK * DERINLIK * YUKSEKLIK)) * 100
    return round(oran, 2)

def destek_var_mi(x, z, w, d, y):
    if y == 0:
        return True
    destek_alan = 0
    gereken_alan = w * d
    for urun in yerlesen_urunler:
        ux, uy, uz = urun["konum"]
        ug, uh, ud = urun["genislik"], urun["yukseklik"], urun["derinlik"]
        if abs((uy + uh) - y) < 1e-6:
            x1, x2 = x, x + w
            z1, z2 = z, z + d
            ux1, ux2 = ux, ux + ug
            uz1, uz2 = uz, uz + ud
            x_overlap = max(0, min(x2, ux2) - max(x1, ux1))
            z_overlap = max(0, min(z2, uz2) - max(z1, uz1))
            destek_alan += x_overlap * z_overlap
    return destek_alan >= gereken_alan * 0.8

def cakisma_var_mi(yeni_urun):
    x1, y1, z1 = yeni_urun["konum"]
    w1, h1, d1 = yeni_urun["genislik"], yeni_urun["yukseklik"], yeni_urun["derinlik"]
    for urun in yerlesen_urunler:
        x2, y2, z2 = urun["konum"]
        w2, h2, d2 = urun["genislik"], urun["yukseklik"], urun["derinlik"]
        if abs(y1 - y2) < 1e-6:
            if (x1 < x2 + w2 and x1 + w1 > x2) and (z1 < z2 + d2 and z1 + d1 > z2):
                return True
    return False

# Görselleştirme fonksiyonu

def gorsel_guncelle():
    fig = go.Figure()

    for i, urun in enumerate(yerlesen_urunler):
        x0, y0, z0 = urun["konum"]
        dx, dy, dz = urun["genislik"], urun["yukseklik"], urun["derinlik"]
        renk = 'gold' if i == len(yerlesen_urunler) - 1 else 'plum'
        opaklik = 1.0 if i == len(yerlesen_urunler) - 1 else 0.8

        x = [x0, x0+dx, x0+dx, x0,     x0,     x0+dx, x0+dx, x0]
        y = [z0, z0,    z0+dz, z0+dz,  z0,     z0,    z0+dz, z0+dz]
        z = [y0, y0,    y0,    y0,     y0+dy,  y0+dy, y0+dy, y0+dy]

        i_faces = [0, 0, 1, 2, 7, 7, 2, 2, 0, 0, 0, 0]
        j_faces = [1, 4, 2, 5, 6, 4, 3, 6, 3, 1, 3, 4]
        k_faces = [5, 5, 5, 6, 5, 5, 7, 7, 2, 2, 7, 7]


        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=i_faces, j=j_faces, k=k_faces,
            color=renk,
            opacity=opaklik,
            flatshading=True,
            lighting=dict(ambient=0.6, diffuse=0.5),
            hovertext=f"Ürün: {urun['id']}<br>{dx}x{dy}x{dz} cm<br>{urun['agirlik']} kg",
            hoverinfo='text'
        ))

    oran = hacim_doluluk_orani()
    renk = "green" if oran > 10 else ("orange" if oran > 5 else "red")

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Genişlik (X)', range=[0, GENISLIK]),
            yaxis=dict(title='Derinlik (Z)', range=[0, DERINLIK]),
            zaxis=dict(title='Yükseklik (Y)', range=[0, YUKSEKLIK]),
            aspectratio=dict(x=1.2, y=1.0, z=1.5),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.0), up=dict(x=0, y=0, z=1))
        ),
        title=dict(
            text=f"{tasima_birimi.upper()}",
            font=dict(size=24),
            x=0.5,
            xanchor='center'
        ),
        annotations=[
            dict(
                text=f"📊 Hacim doluluk oranı: %{oran}",
                x=0.5, y=1,
                xref="paper", yref="paper",
                showarrow=False,
                font=dict(size=25, color=renk),
                align="center"
            )
        ],
        margin=dict(l=0, r=0, t=40, b=0)
    )

    fig.write_html("output.html")  # Sonuçları dışa aktar

# İteratif yerleştirme fonksiyonu
def iteratif_yer_bul(urun, grid=5):
    yukseklik_katmanlari = sorted(set([0] + [u["konum"][1] + u["yukseklik"] for u in yerlesen_urunler]))
    for y in yukseklik_katmanlari:
        if y + urun["yukseklik"] > YUKSEKLIK:
            continue

        # Tüm grid noktalarını sırayla tarar
        for x in range(0, GENISLIK - urun["genislik"] + 1, grid):
            for z in range(0, DERINLIK - urun["derinlik"] + 1, grid):
                temp = {**urun, "konum": (x, y, z)}
                if not cakisma_var_mi(temp) and destek_var_mi(x, z, urun["genislik"], urun["derinlik"], y):
                    return (x, y, z)
    return None

# Ürün yerleştir fonksiyonu (yeni iteratif sistem entegre)
def urun_yerlestir(barkod):
    global toplam_agirlik
    if barkod not in product_catalog:
        print(f"❌ Barkod {barkod} bulunamadı.")
        return

    urun = product_catalog[barkod]
    if toplam_agirlik + urun["agirlik"] > MAX_AGIRLIK:
        print(f"❌ {urun['id']} için ağırlık limiti aşılıyor.")
        return

    konum = iteratif_yer_bul(urun)
    if konum:
        temp = {**urun, "konum": konum}
        yerlesen_urunler.append(temp)
        toplam_agirlik += urun["agirlik"]
        gorsel_guncelle()
        print(f"📦 Ürün yerleştirildi: {urun['id']} at {konum}")
    else:
        print(f"❌ {urun['id']} için uygun yer bulunamadı.")

# Örnek çalıştırma: Tüm ürünleri ağırlık sırasına göre iteratif yerleştirme

if __name__ == "__main__":
    while True:
        secim = input("🚚 Taşıma birimi seçin (palet / rulot): ").strip().lower()
        if secim in tasima_birimleri:
            tasima_birimi = secim
            GENISLIK = tasima_birimleri[secim]["genislik"]
            DERINLIK = tasima_birimleri[secim]["derinlik"]
            YUKSEKLIK = tasima_birimleri[secim]["yukseklik"]
            MAX_AGIRLIK = tasima_birimleri[secim]["max_agirlik"]
            bosluklar = [(0, 0, GENISLIK, DERINLIK)]
            print(f"✅ {secim.upper()} bilgileri yüklendi: {GENISLIK}x{DERINLIK}x{YUKSEKLIK} cm, Max ağırlık: {MAX_AGIRLIK} kg")
            break
        else:
            print("❌ Geçersiz seçim. Lütfen 'palet' ya da 'rulot' yazın.")

    giris = input("📦 Barkodları virgülle ayırarak girin (örn: 1,2,3): ")
    barkod_listesi = sorted([b.strip() for b in giris.split(",") if b.strip() in product_catalog],
                            key=lambda b: product_catalog[b]["agirlik"], reverse=True)

    print(f"\n✅ {len(barkod_listesi)} ürün yüklendi. Her Enter'a bastığında sıradaki ürün eklenecek.")

    index = 0
    while index < len(barkod_listesi):
        input(f"\n▶️ Devam etmek için Enter'a basın (Kalan: {len(barkod_listesi) - index})")
        urun_yerlestir(barkod_listesi[index])
        index += 1

    print("\n✅ Tüm ürünler başarıyla yerleştirildi.")
    print(f"📦 Son doluluk oranı: %{hacim_doluluk_orani()} | Toplam ağırlık: {toplam_agirlik} kg")

