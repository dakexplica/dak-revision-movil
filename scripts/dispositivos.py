"""Matriz de dispositivos de dak-revision-movil.

Medidas en píxeles CSS (los que "ve" la página). El alto es el ÁREA VISIBLE real
(pantalla menos barras del navegador), no la pantalla completa: así las capturas
enseñan lo mismo que ve una persona al abrir el link.

Para añadir un dispositivo: copia una línea y cambia los números. Nada más.
"""

UA_IOS = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 "
          "(KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1")
# iPadOS Safari se presenta como Mac por defecto ("sitio de escritorio"): justo por eso
# las páginas que detectan "móvil" por el user-agent le sirven la versión de compu al iPad.
UA_IPAD = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
           "(KHTML, like Gecko) Version/18.5 Safari/605.1.15")
UA_ANDROID = ("Mozilla/5.0 (Linux; Android 15; SM-S931B) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36")
UA_ANDROID_TABLET = ("Mozilla/5.0 (Linux; Android 15; SM-X710) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
UA_MAC = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
UA_WIN = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")

# clave: (nombre bonito, ancho, alto visible, densidad, plataforma, tipo, user-agent)
#   plataforma: ios | android | escritorio  (decide umbrales: 44px iPhone, 48px Android)
#   tipo: telefono | tableta | compu
DISPOSITIVOS = {
    # ---------------- Teléfonos ----------------
    "iphone-se":        ("iPhone SE / mini (chico)",          375, 553, 2,     "ios",     "telefono", UA_IOS),
    "iphone":           ("iPhone 16/17",                      402, 716, 3,     "ios",     "telefono", UA_IOS),
    "iphone-max":       ("iPhone 17 Pro Max",                 440, 790, 3,     "ios",     "telefono", UA_IOS),
    "android-chico":    ("Android chico (Galaxy A, Moto)",    360, 712, 3,     "android", "telefono", UA_ANDROID),
    "android":          ("Android grande (Pixel, Galaxy S)",  412, 839, 2.625, "android", "telefono", UA_ANDROID),
    "plegable":         ("Galaxy Z Fold cerrado (angosto)",   344, 790, 2.625, "android", "telefono", UA_ANDROID),
    "iphone-acostado":  ("iPhone acostado (horizontal)",      874, 370, 3,     "ios",     "telefono", UA_IOS),
    # ---------------- Tabletas ----------------
    "ipad-mini":        ("iPad mini",                         744, 1062, 2,    "ios",     "tableta",  UA_IPAD),
    "ipad":             ("iPad / iPad Air vertical",          820, 1110, 2,    "ios",     "tableta",  UA_IPAD),
    "ipad-acostado":    ("iPad horizontal",                  1180, 750, 2,     "ios",     "tableta",  UA_IPAD),
    "tablet-android":   ("Galaxy Tab vertical",               800, 1200, 2,    "android", "tableta",  UA_ANDROID_TABLET),
    # ---------------- Compus (Mac y Windows) ----------------
    "laptop-chica":     ("Laptop Windows 1366",              1366, 650, 1,     "escritorio", "compu", UA_WIN),
    "macbook-air":      ("MacBook Air 13\"",                 1470, 830, 2,     "escritorio", "compu", UA_MAC),
    "macbook-pro":      ("MacBook Pro 16\"",                 1728, 990, 2,     "escritorio", "compu", UA_MAC),
    "monitor":          ("Monitor grande / iMac",            2560, 1300, 1,    "escritorio", "compu", UA_MAC),
}

GRUPOS = {
    "completo": list(DISPOSITIVOS),
    "rapido": ["iphone", "android-chico", "ipad", "macbook-air"],
    "telefonos": [k for k, v in DISPOSITIVOS.items() if v[5] == "telefono"],
    "tabletas": [k for k, v in DISPOSITIVOS.items() if v[5] == "tableta"],
    "compus": [k for k, v in DISPOSITIVOS.items() if v[5] == "compu"],
    "mac": ["macbook-air", "macbook-pro", "monitor"],
    "moviles": [k for k, v in DISPOSITIVOS.items() if v[5] != "compu"],
}


def resolver(spec: str):
    """'completo' | 'rapido' | 'telefonos,mac' | 'iphone,android' -> lista de claves sin repetir."""
    claves = []
    for parte in [p.strip() for p in (spec or "completo").split(",") if p.strip()]:
        if parte in GRUPOS:
            claves += GRUPOS[parte]
        elif parte in DISPOSITIVOS:
            claves.append(parte)
        else:
            raise SystemExit(f"Dispositivo o grupo desconocido: '{parte}'. Opciones: "
                             f"{', '.join(GRUPOS)} o {', '.join(DISPOSITIVOS)}")
    vistos, salida = set(), []
    for c in claves:
        if c not in vistos:
            vistos.add(c)
            salida.append(c)
    return salida


def contexto_playwright(clave: str) -> dict:
    nombre, w, h, dpr, plat, tipo, ua = DISPOSITIVOS[clave]
    tactil = tipo != "compu"
    return {
        "viewport": {"width": w, "height": h},
        "screen": {"width": w, "height": h},
        "device_scale_factor": dpr,
        # is_mobile hace que Chromium respete <meta viewport> y use barras de scroll
        # superpuestas, como en un teléfono/tableta de verdad (iPad incluido).
        "is_mobile": tactil,
        "has_touch": tactil,
        "user_agent": ua,
        "locale": "es-ES",
    }


if __name__ == "__main__":
    for g, ks in GRUPOS.items():
        print(f"{g:10} {', '.join(ks)}")
    print()
    for k, v in DISPOSITIVOS.items():
        print(f"{k:16} {v[0]:34} {v[1]}×{v[2]}  dpr {v[3]}  {v[4]}/{v[5]}")


def args_navegador():
    """En Mac usa la GPU de verdad (Metal): el 3D/WebGL va ~10x más rápido y a FPS reales.
    Sin esto Chromium dibuja por software (SwiftShader) y un 3D tarda ~45 s por captura."""
    import platform
    if platform.system() == "Darwin":
        return ["--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist"]
    return ["--ignore-gpu-blocklist"]
