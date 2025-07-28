import pygame
import random
import math

EKRAN_GENISLIGI = 800
EKRAN_YUKSEKLIGI = 600
FPS = 60

DUNYA_GENISLIGI = 6000
DUNYA_YUKSEKLIGI = 6000


SIYAH = (0, 0, 0)
ARKA_PLAN = (240, 248, 255)

# Ayarlar
OYUNCU_BASLANGIC_YARI_CAPI = 20
YEM_SAYISI = 300
YEM_YARI_CAPI = 7
DUSMAN_SAYISI = 25
DUSMAN_MIN_YARI_CAP = 10
DUSMAN_MAX_YARI_CAP = 150


class Kamera:
    def __init__(self, genislik, yukseklik):
        self.x = 0
        self.y = 0
        self.genislik = genislik
        self.yukseklik = yukseklik
        self.zoom = 1.0

    def update(self, hedef):
        self.zoom = max(0.4, min(1.5, 100 / hedef.yari_cap))  
        self.x = hedef.x - (EKRAN_GENISLIGI / self.zoom) / 2
        self.y = hedef.y - (EKRAN_YUKSEKLIGI / self.zoom) / 2

        self.x = max(0, min(self.x, DUNYA_GENISLIGI - self.genislik / self.zoom))
        self.y = max(0, min(self.y, DUNYA_YUKSEKLIGI - self.yukseklik / self.zoom))


class Hucre(pygame.sprite.Sprite):
    def __init__(self, x, y, yari_cap, renk):
        super().__init__()
        self.x = x
        self.y = y
        self.yari_cap = yari_cap
        self.renk = renk
        self.update_rect()

    def update_rect(self):
        self.rect = pygame.Rect(self.x - self.yari_cap, self.y - self.yari_cap, self.yari_cap * 2, self.yari_cap * 2)

    def draw(self, yuzey, kamera):
        ekran_x = (self.x - kamera.x) * kamera.zoom
        ekran_y = (self.y - kamera.y) * kamera.zoom
        ekran_yaricap = self.yari_cap * kamera.zoom

        if -ekran_yaricap < ekran_x < EKRAN_GENISLIGI + ekran_yaricap and \
           -ekran_yaricap < ekran_y < EKRAN_YUKSEKLIGI + ekran_yaricap:
            pygame.draw.circle(yuzey, self.renk, (int(ekran_x), int(ekran_y)), int(ekran_yaricap))


class Oyuncu(Hucre):
    def __init__(self, x, y, yari_cap, renk):
        super().__init__(x, y, yari_cap, renk)

    def update(self, fare_x, fare_y, kamera):
        dx = (fare_x - EKRAN_GENISLIGI / 2) / kamera.zoom
        dy = (fare_y - EKRAN_YUKSEKLIGI / 2) / kamera.zoom

        mesafe = math.hypot(dx, dy)
        if mesafe > 1:
            dx /= mesafe
            dy /= mesafe
            hiz = 40 / math.sqrt(self.yari_cap)
            self.x += dx * hiz
            self.y += dy * hiz

        self.x = max(self.yari_cap, min(self.x, DUNYA_GENISLIGI - self.yari_cap))
        self.y = max(self.yari_cap, min(self.y, DUNYA_YUKSEKLIGI - self.yari_cap))
        self.update_rect()

    def ye(self, diger):
        alan = math.pi * self.yari_cap**2 + math.pi * diger.yari_cap**2
        self.yari_cap = math.sqrt(alan / math.pi)
        diger.kill()


class Dusman(Hucre):
    def __init__(self, x, y, yari_cap, renk):
        super().__init__(x, y, yari_cap, renk)
        self.hiz = random.uniform(1, 3)
        self.hedef_x = random.randint(0, DUNYA_GENISLIGI)
        self.hedef_y = random.randint(0, DUNYA_YUKSEKLIGI)

    def update(self):
        dx = self.hedef_x - self.x
        dy = self.hedef_y - self.y
        mesafe = math.hypot(dx, dy)

        if mesafe < self.yari_cap:
            self.hedef_x = random.randint(0, DUNYA_GENISLIGI)
            self.hedef_y = random.randint(0, DUNYA_YUKSEKLIGI)
        else:
            dx /= mesafe
            dy /= mesafe
            self.x += dx * self.hiz
            self.y += dy * self.hiz

        self.update_rect()

    def ye(self, diger):
        alan = math.pi * self.yari_cap**2 + math.pi * diger.yari_cap**2
        self.yari_cap = math.sqrt(alan / math.pi)
        diger.kill()


def oyun():
    pygame.init()
    ekran = pygame.display.set_mode((EKRAN_GENISLIGI, EKRAN_YUKSEKLIGI))
    pygame.display.set_caption("Agar.io - Zoom Edition")
    saat = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    kamera = Kamera(EKRAN_GENISLIGI, EKRAN_YUKSEKLIGI)

    yemler = pygame.sprite.Group()
    dusmanlar = pygame.sprite.Group()
    tum_hucreler = pygame.sprite.Group()

    oyuncu = Oyuncu(DUNYA_GENISLIGI // 2, DUNYA_YUKSEKLIGI // 2, OYUNCU_BASLANGIC_YARI_CAPI, (0, 150, 255))
    tum_hucreler.add(oyuncu)

    for _ in range(YEM_SAYISI):
        yem = Hucre(
            random.randint(0, DUNYA_GENISLIGI),
            random.randint(0, DUNYA_YUKSEKLIGI),
            YEM_YARI_CAPI,
            (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        )
        yemler.add(yem)
        tum_hucreler.add(yem)

    for _ in range(DUSMAN_SAYISI):
        dusman = Dusman(
            random.randint(0, DUNYA_GENISLIGI),
            random.randint(0, DUNYA_YUKSEKLIGI),
            random.randint(DUSMAN_MIN_YARI_CAP, DUSMAN_MAX_YARI_CAP),
            (random.randint(150, 200), 0, 0)
        )
        dusmanlar.add(dusman)
        tum_hucreler.add(dusman)

    oyun_bitti = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if oyun_bitti and event.type == pygame.MOUSEBUTTONDOWN:
                oyun()  
                return

        if not oyun_bitti:
            fare_x, fare_y = pygame.mouse.get_pos()
            oyuncu.update(fare_x, fare_y, kamera)

            for dusman in dusmanlar:
                dusman.update()
                for yem in pygame.sprite.spritecollide(dusman, yemler, False, pygame.sprite.collide_circle):
                    dusman.ye(yem)

            for yem in pygame.sprite.spritecollide(oyuncu, yemler, False, pygame.sprite.collide_circle):
                oyuncu.ye(yem)

            for dusman in pygame.sprite.spritecollide(oyuncu, dusmanlar, False, pygame.sprite.collide_circle):
                if oyuncu.yari_cap > dusman.yari_cap * 1.1:
                    oyuncu.ye(dusman)
                elif dusman.yari_cap > oyuncu.yari_cap * 1.1:
                    oyun_bitti = True

            kamera.update(oyuncu)

        ekran.fill(ARKA_PLAN)

        for hucre in tum_hucreler:
            hucre.draw(ekran, kamera)

        ekran.blit(font.render(f"Skor: {int(oyuncu.yari_cap)}", True, SIYAH), (10, 10))

        if oyun_bitti:
            yazi = font.render("OYUN BITTI", True, (200, 0, 0))
            ekran.blit(yazi, (EKRAN_GENISLIGI / 2 - yazi.get_width() / 2, EKRAN_YUKSEKLIGI / 2 - yazi.get_height() / 2))

            alt_yazi = font.render("Yeniden başlamak için tıkla", True, (100, 0, 0))
            ekran.blit(alt_yazi, (EKRAN_GENISLIGI / 2 - alt_yazi.get_width() / 2, EKRAN_YUKSEKLIGI / 2 + 40))

        pygame.display.flip()
        saat.tick(FPS)


if __name__ == "__main__":
    oyun()
