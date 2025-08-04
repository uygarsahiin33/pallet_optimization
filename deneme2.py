import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import plotly.graph_objects as go

# Palet boyutları (cm)
PALET_GENISLIK = 120
PALET_DERINLIK = 100
PALET_YUKSEKLIK = 180
PALET_MAX_AGIRLIK = 10000

# Barkodlu ürün kataloğu
product_catalog = {
    "111": {"id": "A", "genislik": 60, "derinlik": 40, "yukseklik": 30, "agirlik": 50},
    "123": {"id": "A", "genislik": 60, "derinlik": 40, "yukseklik": 60, "agirlik": 50},
    "222": {"id": "B", "genislik": 40, "derinlik": 30, "yukseklik": 20, "agirlik": 30},
    "333": {"id": "C", "genislik": 30, "derinlik": 20, "yukseklik": 25, "agirlik": 10},
    "444": {"id": "D", "genislik": 50, "derinlik": 50, "yukseklik": 50, "agirlik": 70},
    "555": {"id": "E", "genislik": 20, "derinlik": 20, "yukseklik": 20, "agirlik": 5},
    "666": {"id": "F", "genislik": 30, "derinlik": 60, "yukseklik": 20, "agirlik": 40},
}

yerlesen_urunler = []
toplam_agirlik = 0
katman_y = 0  # Yükseklik
bosluklar = [(0, 0, PALET_GENISLIK, PALET_DERINLIK)]  # x, z, genişlik, derinlik

def gorsel_guncelle():
    fig = go.Figure()

    for i, urun in enumerate(yerlesen_urunler):
        x0, y0, z0 = urun["konum"]
        dx, dy, dz = urun["genislik"], urun["yukseklik"], urun["derinlik"]
        renk = 'red' if i == len(yerlesen_urunler) - 1 else 'grey'
        opaklik = 1.0 if i == len(yerlesen_urunler) - 1 else 0.6

        # Köşe noktaları: sırasıyla 8 nokta
        x = [x0, x0+dx, x0+dx, x0,     x0,     x0+dx, x0+dx, x0]
        y = [z0, z0,    z0+dz, z0+dz,  z0,     z0,    z0+dz, z0+dz]
        z = [y0, y0,    y0,    y0,     y0+dy,  y0+dy, y0+dy, y0+dy]

        i_faces = [0, 0, 0, 1, 1, 2, 3, 4, 4, 5, 6, 7]
        j_faces = [1, 2, 4, 2, 5, 3, 7, 5, 0, 6, 2, 6]
        k_faces = [2, 4, 5, 5, 6, 0, 6, 1, 3, 7, 6, 4]

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

        # Kenar çizgilerini Scatter3d ile ekle
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # alt taban
            (4, 5), (5, 6), (6, 7), (7, 4),  # üst taban
            (0, 4), (1, 5), (2, 6), (3, 7)   # dikey kenarlar
        ]
        for start, end in edges:
            fig.add_trace(go.Scatter3d(
                x=[x[start], x[end]],
                y=[y[start], y[end]],
                z=[z[start], z[end]],
                mode="lines",
                line=dict(color = 'black' if i == len(yerlesen_urunler) - 1 else 'grey', width=4),
                showlegend=False
            ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Genişlik (X)', range=[0, PALET_GENISLIK]),
            yaxis=dict(title='Derinlik (Z)', range=[0, PALET_DERINLIK]),
            zaxis=dict(title='Yükseklik (Y)', range=[0, PALET_YUKSEKLIK]),
            aspectratio=dict(x=1.2, y=1.0, z=1.5),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.0),
                up=dict(x=0, y=0, z=1)
            )
        ),
        title="Palet Üzerindeki Ürün Yerleşimi (Son Ürün Turuncu)",
        margin=dict(l=0, r=0, t=40, b=0)
    )

    fig.show()


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

    return destek_alan >= gereken_alan * 0.99

def uygun_yer_bul(urun):
    global bosluklar
    for i, (x0, z0, w, d) in enumerate(bosluklar):
        if urun["genislik"] <= w and urun["derinlik"] <= d:
            sağ = (x0 + urun["genislik"], z0, w - urun["genislik"], urun["derinlik"])
            alt = (x0, z0 + urun["derinlik"], w, d - urun["derinlik"])
            bosluklar.pop(i)
            if sağ[2] > 0 and sağ[3] > 0:
                bosluklar.append(sağ)
            if alt[2] > 0 and alt[3] > 0:
                bosluklar.append(alt)
            return (x0, katman_y, z0)
    return None

def barkod_gir(barkod):
    global toplam_agirlik, katman_y, bosluklar

    if barkod not in product_catalog:
        print(f"❌ Barkod {barkod} bulunamadı.")
        return

    urun = product_catalog[barkod]

    if toplam_agirlik + urun["agirlik"] > PALET_MAX_AGIRLIK:
        print(f"❌ {urun['id']} için ağırlık limiti aşılıyor.")
        return

    # Önce mevcut katmana yerleşebiliyor mu?
    konum = uygun_yer_bul(urun)
    if konum and destek_var_mi(konum[0], konum[2], urun["genislik"], urun["derinlik"], konum[1]):
        yerlesen_urunler.append({**urun, "konum": konum})
        toplam_agirlik += urun["agirlik"]
        gorsel_guncelle()
        return

    # Yeni katman yüksekliği hesapla
    aynı_kattaki_urunler = [u for u in yerlesen_urunler if u["konum"][1] == katman_y]
    if aynı_kattaki_urunler:
        yeni_y = katman_y + max(u["yukseklik"] for u in aynı_kattaki_urunler)
    else:
        yeni_y = katman_y + 10  # varsayılan artış

    if yeni_y + urun["yukseklik"] > PALET_YUKSEKLIK:
        print(f"❌ {urun['id']} için yükseklik limiti aşılıyor.")
        return

    # Yeni katman oluştur ve dene
    katman_y = yeni_y
    bosluklar = [(0, 0, PALET_GENISLIK, PALET_DERINLIK)]
    konum = uygun_yer_bul(urun)
    if konum and destek_var_mi(konum[0], konum[2], urun["genislik"], urun["derinlik"], konum[1]):
        yerlesen_urunler.append({**urun, "konum": konum})
        toplam_agirlik += urun["agirlik"]
        gorsel_guncelle()
        return

    # 🔁 Tüm yükseklikleri (önceki katmanları) sırayla dene (yüksekten 0'a doğru)
    y_degerleri = sorted({u["konum"][1] + u["yukseklik"] for u in yerlesen_urunler}, reverse=True)
    for y_start in y_degerleri:
        if y_start + urun["yukseklik"] > PALET_YUKSEKLIK:
            continue

        # Yeni geçici katman
        gecici_katman = y_start
        gecici_bosluklar = [(0, 0, PALET_GENISLIK, PALET_DERINLIK)]
        konum = uygun_yer_bul(urun)
        if konum:
            # override y değeri
            konum = (konum[0], gecici_katman, konum[2])
            if destek_var_mi(konum[0], konum[2], urun["genislik"], urun["derinlik"], konum[1]):
                yerlesen_urunler.append({**urun, "konum": konum})
                toplam_agirlik += urun["agirlik"]
                gorsel_guncelle()
                return

    print(f"❌ {urun['id']} için hiçbir katmanda uygun destek ve yer bulunamadı.")


# ▶️ Yeni giriş sistemi: toplu giriş ve adım adım çizim
if __name__ == "__main__":
    giris = input("📦 Barkodları virgülle ayırarak girin (örn: 111,123,222): ")
    barkod_listesi = [b.strip() for b in giris.split(",") if b.strip() in product_catalog]

    print(f"\n✅ {len(barkod_listesi)} ürün yüklendi. Her Enter'a bastığında sıradaki ürün eklenecek.")

    index = 0
    while index < len(barkod_listesi):
        input(f"\n▶️ Devam etmek için Enter'a basın (Kalan: {len(barkod_listesi) - index})")
        barkod_gir(barkod_listesi[index])
        index += 1

    print("\n✅ Tüm ürünler başarıyla yerleştirildi.")
