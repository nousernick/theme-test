#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera tdSimple-Texto.xml a partir de tdSimple.xml:
version del theme Blogspot centrada en TEXTO PURO.
Se retiran todas las funciones, complementos y plugins pensados para imagenes
(slider Orbit, galeria Clearing, Joyride, RefineSlide/imagesLoaded, Holder,
miniaturas de entradas, avatares, imagenes de cabecera, FitVids, etc.).
"""
import re

SRC = '/workspace/tdSimple.xml'
DST = '/workspace/tdSimple-Texto.xml'

s = open(SRC, encoding='utf-8').read()
removed = []

def sub_once(pattern, repl, label, flags=0):
    """Reemplazo por expresion regular; falla si no hay exactamente 1 coincidencia."""
    global s
    rx = re.compile(pattern, flags)
    hits = rx.findall(s)
    assert len(hits) == 1, '%s -> %d coincidencias (esperadas 1)' % (label, len(hits))
    s = rx.sub(repl, s, count=1)
    removed.append(label)

def cut_between(marker_start, marker_end, label):
    global s
    i = s.find(marker_start)
    assert i != -1, 'no encontrado (inicio): ' + label
    j = s.find(marker_end, i)
    assert j != -1, 'no encontrado (fin): ' + label
    s = s[:i] + s[j:]
    removed.append(label)

# ---------------------------------------------------------------- HEAD / CSS
# 1) Font Awesome (solo se usaba para glifos de iconos; se sustituyen por texto)
sub_once(r"<link href='//netdna\.bootstrapcdn\.com/font-awesome[^>]*>\n", '',
         'head: link Font Awesome')

# 2) IE8 shims (HTML5 Shiv + Respond.js)
cut_between('<!-- HTML5 shim and Respond.js', '<b:skin>',
            'head: HTML5Shiv + Respond.js (compatibilidad IE8)')

# 3) Regla de pantalla de diseno para el slider eliminado
sub_once(r"body#layout #slider \{display:none;\}\n", '', 'css: body#layout #slider')

# 4) border-radius aplicado a miniaturas/imagenes alineadas
sub_once(
    r"""\.main-navigationpbt,\n\.border-radius-small,\n\.post-thumb img,\nimg\.alignleft,\nimg\.alignright,\nimg\.aligncenter,\nimg\.alignnone \{""",
    """.main-navigationpbt,
.border-radius-small {""",
    'css: selectores .post-thumb img / img.align* (border-radius)')

# 5) Margenes de imagenes alineadas dentro de entradas
sub_once(
    r"""img\.alignleft \{\n\tmargin: 15px 25px 15px 0;\n\}\n\nimg\.alignright \{\n\tmargin: 15px 0 15px 25px;\n\}\n\nimg\.aligncenter \{\n\tmargin: 15px auto;\n\}\n\nimg\.alignnone \{\n    display: block;\n    margin: 15px 0;\n\}\n\n""",
    '', 'css: bloque img.align* (=Media)')

# 6) Estilo de la miniatura insertada por createSummaryAndThumb
sub_once(
    r"""\.pbtthumbimg \{\n  background: #fff;\n  border: 0 solid #eee;\n  float: none;\n  margin: 0 auto 10px;\n  max-width: 100%;\n  height: auto;\n  padding: 0 !important;\n\}\n\n""",
    '', 'css: .pbtthumbimg')

# ------------------------------------------------------------------ SCRIPTS
# 7) Variables de configuracion de resumenes con miniatura
sub_once(
    r"""<script type='text/javascript'>\nsummary_noimg = 400;\nsummary_img = 300;\nimg_thumb_height = 150;\nimg_thumb_width = 200; ?\n</script>\n""",
    '', 'js: variables summary_noimg/summary_img/img_thumb_*')

# 8) createSummaryAndThumb -> resumen de TEXTO puro (recorta a 400 caracteres)
i_fn = s.find('function createSummaryAndThumb(pID){')
assert i_fn != -1, 'no encontrado: createSummaryAndThumb'
i_end = s.find('\n}', i_fn)
assert i_end != -1
s = (s[:i_fn] +
     'function createSummaryAndThumb(pID){\n'
     '\tvar div = document.getElementById(pID);\n'
     '\t/* Solo texto: resumen sin miniaturas ni imagenes */\n'
     '\tdiv.innerHTML = removeHtmlTag(div.innerHTML, 400);\n}' +
     s[i_end+2:])
removed.append('js: createSummaryAndThumb (ahora solo texto)')

# ------------------------------------------------------------------- WIDGETS
# 9) Cabecera: eliminar por completo las ramas de imagen del widget Header
hdr = s.find("<b:widget id='Header1'")
assert hdr != -1
main_i = s.find("<b:includable id='main'>", hdr)
desc_i = s.find("<b:includable id='description'>", hdr)
assert main_i != -1 and desc_i != -1
s = (s[:main_i] +
     "<b:includable id='main'>\n"
     "  <!-- Solo texto: la cabecera nunca muestra imagen -->\n"
     "  <div id='header-inner'>\n"
     "    <div class='titlewrapper'>\n"
     "      <h1 class='site-title'>\n"
     "        <b:include name='title'/>\n"
     "      </h1>\n"
     "    </div>\n"
     "    <b:if cond='data:description'>\n"
     "      <h2 class='site-description'><data:description/></h2>\n"
     "    </b:if>\n"
     "  </div>\n"
     "</b:includable>\n    " +
     s[desc_i:])
removed.append('widget Header1: sin imagen de cabecera (ni fondo REPLACE)')

# 10) Backlinks: icono gif de borrado -> enlace de texto
sub_once(
    r"""<a expr:href='data:backlink\.deleteUrl' expr:title='data:top\.deleteBacklinkMsg'>\n\s*<img src='//www\.blogger\.com/img/icon_delete13\.gif'/>\n\s*</a>""",
    "<a class='backlink-delete' expr:href='data:backlink.deleteUrl' expr:title='data:top.deleteBacklinkMsg'>[x]</a>",
    'blog: backlinkDeleteIcon sin imagen')

# 11) Comentarios: icono gif de borrado -> enlace de texto
sub_once(
    r"""<a class='comment-delete' expr:href='data:comment\.deleteUrl' expr:title='data:top\.deleteCommentMsg'>\n\s*<img src='//www\.blogger\.com/img/icon_delete13\.gif'/>\n\s*</a>""",
    "<a class='comment-delete' expr:href='data:comment.deleteUrl' expr:title='data:top.deleteCommentMsg'>[x]</a>",
    'blog: commentDeleteIcon sin imagen')

# 12) Comentarios: favicon del autor y avatar -> solo nombre de texto
sub_once(
    r"""<b:if cond='data:comment\.favicon'>\n\s*<img expr:src='data:comment\.favicon'[^>]*/>\n\s*</b:if>\n(\s*<a expr:name='data:comment\.anchorName'/>)\n\s*<b:if cond='data:blog\.enabledCommentProfileImages'>\n\s*<data:comment\.authorAvatarImage/>\n\s*</b:if>\n""",
    r"\1\n", 'blog: comentarios sin favicon/avatar')

# 13) Comentarios anidados: quitar avatarUrl (gd$image) del parser JS
sub_once(
    r"""profileUrl: \(auth\.uri \? auth\.uri\.\$t : undefined\),\n\s*avatarUrl: \(auth\.gd\$image \? auth\.gd\$image\.src : undefined\)""",
    "profileUrl: (auth.uri ? auth.uri.$t : undefined)",
    'blog: threaded comments sin avatarUrl')

# 14) Indice movil: miniatura de la entrada -> fuera
sub_once(
    r"""<b:if cond='data:post\.thumbnailUrl'>\n\s*<div class='mobile-index-thumbnail'>\n\s*<div class='Image'>\n\s*<img expr:src='data:post\.thumbnailUrl'/>\n\s*</div>\n\s*</div>\n\s*</b:if>\n\n\s*""",
    '', 'blog: mobile-index-post sin miniatura')

# 15) Popular Posts: eliminar las variantes con miniaturas (showThumbnails)
pp = s.find("<b:widget id='PopularPosts1'")
assert pp != -1
pp_main = s.find("<b:includable id='main'>", pp)
pp_qe = s.find("<b:include name='quickedit'/>", pp_main)
assert pp_main != -1 and pp_qe != -1
s = (s[:pp_main] +
     "<b:includable id='main'>\n"
     "  <b:if cond='data:title'><h2><data:title/></h2></b:if>\n"
     "  <div class='widget-content popular-posts'>\n"
     "    <ul>\n"
     "      <b:loop values='data:posts' var='post'>\n"
     "      <li>\n"
     "        <b:if cond='data:showSnippets == &quot;false&quot;'>\n"
     "          <!-- Solo texto: titulo -->\n"
     "          <a expr:href='data:post.href'><data:post.title/></a>\n"
     "        <b:else/>\n"
     "          <!-- Solo texto: titulo + snippet -->\n"
     "          <div class='item-title'><a expr:href='data:post.href'><data:post.title/></a></div>\n"
     "          <div class='item-snippet'><data:post.snippet/></div>\n"
     "        </b:if>\n"
     "      </li>\n"
     "      </b:loop>\n"
     "    </ul>\n"
     "    " +
     s[pp_qe:])
removed.append('widget PopularPosts1: sin miniaturas (solo titulo/snippet)')

# 16) Plugin FitVids (videos embebidos responsivos) y su llamada
fv = s.find("<script type='text/javascript'>\n//<![CDATA[\n\n/*global jQuery */")
assert fv != -1
fv_end = s.find("//]]>", fv)
fv_end = s.find("</script>", fv_end) + len("</script>\n")
s = s[:fv] + s[fv_end:]
removed.append('js: plugin FitVids (embeds de video)')

sub_once(r'\t*jQuery\("\.hentry"\)\.fitVids\(\);\n\s*\n', '', 'js: llamada fitVids()')

# 17) Mega-bloque de scripts Foundation/ZURB: Modernizr/yepnope, Custom Forms,
#     event.move/swipe, Reveal, Orbit (slider), imageready, Holder, Navigation,
#     Buttons, Tabs, Tooltips, Joyride (tours), Clearing (galerias/lightbox),
#     Magellan y RefineSlide/imagesLoaded (slider de imagenes).
fnd_marker = "/* Modernizr 2.6.2 (Custom Build) | MIT & BSD"
fnd_i = s.find(fnd_marker)
assert fnd_i != -1
fnd_head = s.rfind("<script type='text/javascript'>", 0, fnd_i)
fnd_tail = s.find("</script>", fnd_i) + len("</script>\n")
s = s[:fnd_head] + s[fnd_tail:]
removed.append('js: Modernizr + Foundation completo (Orbit/Clearing/Joyride/Reveal/'
               'RefineSlide/imagesLoaded/Holder/Tooltips/Tabs/Magellan...)')

# 18) Init de Foundation ya no existe; comprobar que no queden llamadas colgadas
assert 'foundationClearing' not in s and '$doc.foundation' not in s

# 19) Iconos Font Awesome -> caracteres de texto plano
sub_once(r"<div id='gotoppbt'><h6><i class='fa fa-arrow-up'/></h6></div>",
         "<div id='gotoppbt'><h6>&#8679;</h6></div>",
         'html: boton "subir" sin Font Awesome')
sub_once(r"<div class='sidebar-buttonpbt'><i class='fa fa-plus'/></div>",
         "<div class='sidebar-buttonpbt'><span>+</span></div>",
         'html: boton sidebar sin Font Awesome')

# 20) Toggle del sidebar: clases foundicon (glifos) -> simbolo de texto
sub_once(r"jQuery\('\.sidebar-buttonpbt i'\)\.removeClass\('foundicon-minus'\)\.addClass\('foundicon-plus'\);",
         "jQuery('.sidebar-buttonpbt span').text('+');",
         'js: toggle sidebar usa texto (+)')
sub_once(r"jQuery\('\.sidebar-buttonpbt i'\)\.removeClass\('foundicon-plus'\)\.addClass\('foundicon-minus'\);",
         "jQuery('.sidebar-buttonpbt span').text('\\u2212');",
         'js: toggle sidebar usa texto (−)')

open(DST, 'w', encoding='utf-8').write(s)
print('Escrito:', DST)
print('Elementos retirados/modificados (%d):' % len(removed))
for r in removed:
    print(' -', r)
