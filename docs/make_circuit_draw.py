import schemdraw
import schemdraw.elements as elm

# 描画キャンバスの初期化
d = schemdraw.Drawing(file='./circuit_v1.svg', show=False)
d.config(fontsize=11, unit=2.8)

# BJTエレメントの互換性処理
if hasattr(elm, 'BjtNpn'):
    BjtClass = elm.BjtNpn
elif hasattr(elm, 'Bjt'):
    BjtClass = elm.Bjt
else:
    BjtClass = getattr(elm, 'Npn', None)

# --------------------------------------------------
# 1. マイコン（ATTINY402）本体の描画
# --------------------------------------------------
uc = d.add(
    elm.Ic(
        pins=[
            elm.IcPin(name='VDD', pin='1', side='top'),
            elm.IcPin(name='GND', pin='8', side='bottom'),
            elm.IcPin(name='UPDI', pin='6', side='left'),
            elm.IcPin(name='PWM', pin='2', side='right'),
            elm.IcPin(name='ADC', pin='3', side='right'),
        ],
        size=(4.0, 4.0),
        pinspacing=1.2,
    ).label('ATTINY402', 'center', fontsize=12)
)

# --------------------------------------------------
# 2. 電源（VDD/GND）とパスコン回路
# --------------------------------------------------
# VDDライン（テキスト位置を左に固定）
d.add(elm.Line().up().at(uc.VDD).length(2.5).label('5V (DPS-150)', 'left', ofst=0.3))
d.add(elm.Dot())

# パスコン (0.1uF) 右に伸ばして綺麗なGNDに直接落とす
d.push()
d.add(elm.Line().right().length(2.0))
d.add(elm.Capacitor().down().label('0.1uF\n(104)', 'right', ofst=0.2))
d.add(elm.Ground())
d.pop()

# マイコンGNDライン
d.add(elm.Line().down().at(uc.GND).length(1.5))
d.add(elm.Ground())

# --------------------------------------------------
# 3. UPDI 書き込み回路（MPLAB SNAP）
# --------------------------------------------------
d.add(elm.Resistor().left().at(uc.UPDI).label('470', 'top'))
d.add(elm.Line().left().length(1.2).label('SNAP Pin 4\n(UPDI)', 'left'))

# --------------------------------------------------
# 4. 発光回路（LED ＋ 制限抵抗）
# --------------------------------------------------
d.add(elm.Resistor().right().at(uc.PWM).label('4.7k', 'top'))
d.add(elm.Line().right().length(1.0))
d.add(elm.LED().down().label('Chip LED (Green)', 'right', ofst=(-0.3, 2.5)))
d.add(elm.Ground())

# --------------------------------------------------
# 5. 受光回路（フォトトランジスタ ＋ プルアップ抵抗）
# --------------------------------------------------
# 横幅をしっかり取ってLED回路やパスコンと離す
d.add(elm.Line().right().at(uc.ADC).length(5.5))
d.add(elm.Dot())

# 上方向：プルアップ抵抗 (100k ohm) -> 5V
d.push()
d.add(elm.Resistor().up().label('100k', 'right', ofst=(-1.6, 0.9)))
d.add(elm.Line().up().length(1.2).label('5V', 'right', ofst=0.2)) # 5Vを右側に配置して100kohmとの重なりを防止
d.pop()

# 下方向：フォトトランジスタ -> GND
pt = d.add(BjtClass().right().anchor('collector'))
pt.label('PT19-21C\n(Photo TR)', 'right', ofst=0.3)
d.add(elm.Line().down().at(pt.emitter).length(1.0))
d.add(elm.Ground())

# SVG保存
d.save('./circuit_v1.svg')
print('Successfully saved to ./circuit_v1.svg')
