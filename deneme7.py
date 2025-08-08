import plotly.graph_objects as go
import pandas as pd

# Taşıma birimleri tanımı
tasima_birimleri = {
    "palet": {"genislik": 120, "derinlik": 100, "yukseklik": 180, "max_agirlik": 1000},
    "rulot": {"genislik": 100, "derinlik": 100, "yukseklik": 216, "max_agirlik": 1000}
}

# Global değişkenler
yerlesen_urunler = []
toplam_agirlik = 0
palet_listesi = []

# Excel'den ürün yükleme
def urunleri_excelden_yukle(dosya_yolu):
    df = pd.read_excel(dosya_yolu)
    product_catalog = {}
    counter = 1
    for index, row in df.iterrows():
        adet = int(row["SİPARİŞ SAYISI"])
        for _ in range(adet):
            product_catalog[str(counter)] = {
                "id": row["MAL NO"],
                "ad": row["MAL ADI"],
                "genislik": int(row["EN"]),
                "derinlik": int(row["BOY"]),
                "yukseklik": int(row["YÜKSEKLİK"]),
                "agirlik": 10  # Şimdilik sabit
            }
            counter += 1
    return product_catalog

# Hacim doluluk oranı
def hacim_doluluk_orani():
    dolu_hacim = sum(u["genislik"] * u["derinlik"] * u["yukseklik"] for u in yerlesen_urunler)
    return round((dolu_hacim / (GENISLIK * DERINLIK * YUKSEKLIK)) * 100, 2)

# Destek kontrolü
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

# Çakışma kontrolü
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

# Görselleştirme
def gorsel_guncelle(palet_no):
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
            color=renk, opacity=opaklik,
            flatshading=True,
            lighting=dict(ambient=0.6, diffuse=0.5),
            hovertext=f"Ürün: {urun['id']}<br>{dx}x{dy}x{dz} cm<br>{urun['agirlik']} kg",
            hoverinfo='text'
        ))
    oran = hacim_doluluk_orani()
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Genişlik (X)', range=[0, GENISLIK]),
            yaxis=dict(title='Derinlik (Z)', range=[0, DERINLIK]),
            zaxis=dict(title='Yükseklik (Y)', range=[0, YUKSEKLIK]),
        ),
        title=f"Palet {palet_no} - Doluluk %{oran}"
    )
    fig.write_html(f"palet_{palet_no}.html")

# Yer bulma
def iteratif_yer_bul(urun, grid=5):
    yukseklik_katmanlari = sorted(set([0] + [u["konum"][1] + u["yukseklik"] for u in yerlesen_urunler]))
    for y in yukseklik_katmanlari:
        if y + urun["yukseklik"] > YUKSEKLIK:
            continue
        for x in range(0, GENISLIK - urun["genislik"] + 1, grid):
            for z in range(0, DERINLIK - urun["derinlik"] + 1, grid):
                temp = {**urun, "konum": (x, y, z)}
                if not cakisma_var_mi(temp) and destek_var_mi(x, z, urun["genislik"], urun["derinlik"], y):
                    return (x, y, z)
    return None

# Ürün yerleştir
def urun_yerlestir(barkod):
    global toplam_agirlik
    urun = product_catalog[barkod]
    if toplam_agirlik + urun["agirlik"] > MAX_AGIRLIK:
        return False
    konum = iteratif_yer_bul(urun)
    if konum:
        temp = {**urun, "konum": konum}
        yerlesen_urunler.append(temp)
        toplam_agirlik += urun["agirlik"]
        return True
    return False

# Ana algoritma
if __name__ == "__main__":
    secim = "palet"
    GENISLIK = tasima_birimleri[secim]["genislik"]
    DERINLIK = tasima_birimleri[secim]["derinlik"]
    YUKSEKLIK = tasima_birimleri[secim]["yukseklik"]
    MAX_AGIRLIK = tasima_birimleri[secim]["max_agirlik"]

    product_catalog = urunleri_excelden_yukle(r"C:\Users\uygar\Desktop\urunler.xlsx")
    barkod_listesi = sorted(product_catalog.keys(), key=lambda b: product_catalog[b]["agirlik"], reverse=True)

    palet_no = 1
    kalan_urunler = barkod_listesi.copy()

    while kalan_urunler:
        print(f"\n📦 Palet {palet_no} başlatılıyor...")
        yerlesen_urunler.clear()
        toplam_agirlik = 0
        yerlestirilemeyenler = []
        for barkod in kalan_urunler:
            if not urun_yerlestir(barkod):
                yerlestirilemeyenler.append(barkod)
        gorsel_guncelle(palet_no)
        print(f"✅ Palet {palet_no} tamamlandı. Doluluk %{hacim_doluluk_orani()} - {toplam_agirlik} kg")
        kalan_urunler = yerlestirilemeyenler
        palet_no += 1
