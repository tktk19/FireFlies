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
            elm.IcPin(name='PWM', pin='5', side='right'),
            elm.IcPin(name='ADC', pin='3', side='right'),
        ],
        size=(4.5, 4.5),
        pinspacing=1.4,
    ).label('ATTINY402', 'center', fontsize=12)
)

# --------------------------------------------------
# 2. 電源（VDD/GND）とパスコン回路
# --------------------------------------------------
# VDDライン
d.add(elm.Line().up().at(uc.VDD).length(1.2))
d.add(elm.Dot())

# パスコン (0.1uF)
d.push()
d.add(elm.Line().right().length(3.0))
d.add(elm.Capacitor().down().label('0.1uF\n(104)', 'right', ofst=0.2))
d.add(elm.Ground())
d.pop()

# メインVCCラインのトップ
d.add(elm.Vdd().label('VCC\n(DPS-150)', 'top'))

# マイコンGNDライン
d.add(elm.Line().down().at(uc.GND).length(1.5))
d.add(elm.Ground())

# --------------------------------------------------
# 3. UPDI 書き込み回路（MPLAB SNAP + プルアップ抵抗）
# --------------------------------------------------
d.add(elm.Dot().at(uc.UPDI))

# VCCプルアップ抵抗（SNAP必須）
d.push()
d.add(elm.Resistor().up().label('4.7k', 'left', ofst=0.2))
d.add(elm.Vdd().label('VCC', 'top'))
d.pop()

# SNAPへの直接接続（直列保護抵抗なし）
d.add(elm.Line().left().length(2.5).label('SNAP Pin 4\n(UPDI)', 'left'))

# --------------------------------------------------
# 4. 発光回路（物理5ピン PWM/PA2 ＋ LED ＋ 制限抵抗）
# --------------------------------------------------
d.add(elm.Resistor().right().at(uc.PWM).label('4.7k', 'top'))
d.add(elm.Line().right().length(1.5))
d.add(elm.LED().down().label('Chip LED\n(Green)', 'left', ofst=0.2))
d.add(elm.Ground())

# --------------------------------------------------
# 5. 受光回路（フォトトランジスタ ＋ プルアップ抵抗）
# --------------------------------------------------
d.add(elm.Line().right().at(uc.ADC).length(7.0))
d.add(elm.Dot())

# プルアップ抵抗 (100k ohm) -> VCC
d.push()
d.add(elm.Resistor().up().label('100k', 'right', ofst=0.2))
d.add(elm.Vdd().label('VCC', 'top'))
d.pop()

# フォトトランジスタ -> GND
pt = d.add(BjtClass().right().anchor('collector'))
pt.label('PT19-21C\n(Photo TR)', 'right', ofst=0.3)
d.add(elm.Line().down().at(pt.emitter).length(1.0))
d.add(elm.Ground())

# SVG保存
d.save('./circuit_v1.svg')
print('Successfully saved to ./circuit_v1.svg')