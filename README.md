# Estudo de Caso – Computação Gráfica 2D: Animação Estilo Stick Fight

**Disciplina:** Computação Gráfica e Processamento de Imagens
**Curso:** Engenharia de Computação
**Aluno:** Jorge Luis de Oliveira Ferrari
**RE:** 1170103026
**Data:** Março de 2026

---

## Sobre o Projeto

Este repositório contém o estudo de caso desenvolvido para a disciplina de Computação Gráfica e Processamento de Imagens. O projeto demonstra a aplicação prática das **transformações geométricas 2D** (translação, rotação, escala e composição) na criação de uma animação de luta entre figuras de palito (stick figures), inspirada no estilo do jogo *Stick Fight: The Game*.

![Posição Idle](docs/images/frame_01_idle.png)

## Estrutura do Repositório

```
stick-fight-cg2d/
├── README.md                    # Este arquivo
├── docs/
│   ├── ESTUDO_DE_CASO.md        # Estudo de caso completo em Markdown
│   ├── Estudo_de_Caso_*.pdf     # Versão PDF para entrega
│   └── images/                  # Ilustrações e diagramas
│       ├── frame_01_idle.png
│       ├── frame_02_soco_windup.png
│       ├── frame_03_soco_impacto.png
│       ├── frame_04_chute.png
│       ├── frame_05_pulo.png
│       ├── frame_06_diagrama.png
│       └── frame_07_articulacoes.png
└── src/
    └── stick_fight_animation.py # Código funcional da animação
```

## Como Executar

### Pré-requisitos

- Python 3.8+
- Pygame 2.0+

### Instalação

```bash
pip install pygame
```

### Executando a Animação

```bash
cd src
python stick_fight_animation.py
```

### Controles

| Tecla | Ação |
|-------|------|
| `R` | Reiniciar a animação |
| `ESC` | Sair |

## Transformações Geométricas Aplicadas

| Transformação | Fórmula | Aplicação no Projeto |
|---------------|---------|---------------------|
| **Translação** | P' = P + T | Movimentação dos personagens, gravidade, partículas |
| **Rotação** | P' = R(θ) · P | Articulações dos membros, animações de ataque |
| **Escala** | P' = S · P | Squash & stretch no impacto dos golpes |
| **Composição** | M = T · R · S | Rotação em torno de articulações (cinemática direta) |

## Screenshots

### Animação de Soco
| Preparação (Wind-up) | Impacto |
|:---:|:---:|
| ![Wind-up](docs/images/frame_02_soco_windup.png) | ![Impacto](docs/images/frame_03_soco_impacto.png) |

### Chute e Pulo
| Chute | Pulo |
|:---:|:---:|
| ![Chute](docs/images/frame_04_chute.png) | ![Pulo](docs/images/frame_05_pulo.png) |

### Diagrama de Transformações
![Diagrama](docs/images/frame_06_diagrama.png)

## Referências

- BROOKSHEAR, J. Glenn. **Ciência da Computação: uma visão abrangente**. 11. ed. Porto Alegre: Bookman, 2013. ISBN: 978-85-8260-031-3.
- FRIGERI, Sandra Rovena. **Computação Gráfica**. Porto Alegre: SAGAH, 2018. ISBN: 978-85-9502-688-9.
- SAÚDE, A. V. **Computação gráfica e processamento de imagens**. 1. ed. Londrina: Editora e Distribuidora Educacional SA, 2019. v. 1. 200p.

## Licença

Este projeto foi desenvolvido para fins acadêmicos.
