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
def script_block_around(marker):
    """Devuelve (inicio, fin) del bloque <script> completo que contiene `marker`."""
    i = s.find(marker)
    assert i != -1, 'no encontrado el marcador: ' + marker
    head = s.rfind("<script", 0, i)
    tail = s.find("</script>", i) + len("</script>\n")
    return head, tail

fv_head, fv_tail = script_block_around("/*global jQuery */\n/*jshint multistr:true browser:true */")
s = s[:fv_head] + s[fv_tail:]
removed.append('js: plugin FitVids (embeds de video)')

sub_once(r'\t*jQuery\("\.hentry"\)\.fitVids\(\);\n\s*\n', '', 'js: llamada fitVids()')

# 17) Mega-bloque de scripts Foundation/ZURB: Modernizr/yepnope, Custom Forms,
#     event.move/swipe, Reveal, Orbit (slider), imageready, Holder, Navigation,
#     Buttons, Tabs, Tooltips, Joyride (tours), Clearing (galerias/lightbox),
#     Magellan y RefineSlide/imagesLoaded (slider de imagenes).
fnd_marker = "/* Modernizr 2.6.2 (Custom Build) | MIT & BSD"
fnd_head, fnd_tail = script_block_around(fnd_marker)
s = s[:fnd_head] + s[fnd_tail:]
removed.append('js: Modernizr + Foundation completo (Orbit/Clearing/Joyride/Reveal/'
               'Holder/Navigation/Buttons/Tabs/Tooltips/Magellan...)')

# 17b) Segundo bloque: init de Foundation ($doc.foundation*), RefineSlide/imagesLoaded
#      (slider de imagenes) y el ready() con fitVids(). Se conserva unicamente la
#      logica de texto del sidebar / boton "subir" / toggles.
rs_marker = "jQuery RefineSlide plugin"
rs_head, rs_tail = script_block_around(rs_marker)
seg = s[rs_head:rs_tail]
keep = []
if 'sidebar-buttonpbt' in seg or 'gotoppbt' in seg:
    keep.append('logica de sidebar/boton subir conservada')
s = s[:rs_head] + s[rs_tail:]
removed.append('js: init Foundation ($doc.foundation*) + RefineSlide/imagesLoaded (slider)')

# El ready() eliminado contenia tambien gotoppbt/sidebar/toggle; los re-añadimos
# en un bloque minimo sin dependencias de imagenes/slider.
readd = """<script type='text/javascript'>
//<![CDATA[
jQuery(document).ready(function(){

\tjQuery('#gotoppbt').click(function() {
\t\tjQuery("html, body").animate({ scrollTop: 0 }, 1000);
\t});

\tjQuery('.sidebar-buttonpbt').click(function() {

\t\tif(jQuery('.widget-innerpbt').is(':visible')) {
\t\t\tjQuery('.sidebar-buttonpbt span').text('+');
\t\t\tjQuery('.widget-innerpbt').fadeOut().css('width', '0');
\t\t} else {
\t\t\tvar currentBrowserWidth = jQuery( window ).width();

\t\t\tif( currentBrowserWidth > 420 ) {
\t\t\t\tsidebarWidth = '420px';
\t\t\t} else {
\t\t\t\tsidebarWidth = currentBrowserWidth.toString() + 'px';
\t\t\t}
\t\t\tjQuery('.sidebar-buttonpbt span').text('\\u2212');
\t\t\tjQuery('.widget-areapbt').css('height','100%');
\t\t\tjQuery('.widget-innerpbt, .widget').fadeIn(300, function() {
\t\t\t\tjQuery('.widget-innerpbt').css('width', sidebarWidth);
\t\t\t});
\t\t}
\t});

\t/* Toggle */
\tjQuery('.toggle-container').find('h5').click(function() {
\t\tjQuery(this).parents('.toggle-container').find('.content').toggle();
\t});

});

jQuery(window).scroll(function(){
\tif (jQuery(this).scrollTop() > 200) {
\t\tjQuery('#gotoppbt').fadeIn();
\t} else {
\t\tjQuery('#gotoppbt').fadeOut();
\t}
});
//]]>
</script>
"""
# Insertar donde estaba el bloque eliminado (antes del cierre </body>)
anchor = s.find('</body>')
assert anchor != -1
s = s[:anchor] + readd + '\n' + s[anchor:]
removed.append('js: re-insercion del ready() minimo (gotop/sidebar/toggle, sin slider)')

# 18) Comprobar que no queden llamadas colgadas a plugins ya retirados
for leftover in ['foundationClearing', '$doc.foundation', 'refineSlide', 'imagesLoaded',
                 'fitVids', 'Modernizr', 'yepnope', 'Holder']:
    assert leftover not in s, 'referencia residual a: ' + leftover

# 18b) CSS muerto: reglas de los complementos de imagen eliminados (Orbit/slider,
#      Clearing/galeria, Joyride/tours, Reveal/modales, Tooltips, Magellan,
#      RefineSlide y wrappers de video fluido). Se purgan del <b:skin>.
KW_CSS = (r'(?:joyride|#joyRideTipContent|orbit|clearing|reveal-modal|magellan|'
          r'tooltip|has-tip|rs-slider|rs-wrap|rs-slide|rs-caption|rs-thumb|rs-grid|'
          r'rs-arrows|refineSlide|fluid-width-video|flexslider|slideshow)')

def css_dead_spans(text, kw):
    """Spans (inicio, fin) de las reglas CSS cuyo selector contiene `kw`
    (incluidas las anidadas dentro de @media)."""
    spans = []
    n = len(text)
    i = 0
    sel_start = 0
    while i < n:
        if text.startswith('/*', i):
            e = text.find('*/', i + 2)
            i = (e + 2) if e != -1 else n
            continue
        c = text[i]
        if c == '{':
            sel = text[sel_start:i]
            depth = 1
            k = i + 1
            while k < n and depth:
                if text.startswith('/*', k):
                    e = text.find('*/', k + 2)
                    k = (e + 2) if e != -1 else n
                    continue
                ch = text[k]
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                k += 1
            is_at = sel.strip().startswith('@')
            if not is_at and re.search(kw, sel, re.I):
                spans.append((sel_start, k))
            elif is_at:
                off = i + 1
                for a, b in css_dead_spans(text[i + 1:k - 1], kw):
                    spans.append((off + a, off + b))
            sel_start = k
            i = k
            continue
        if c == '}':
            sel_start = i + 1
        i += 1
    return spans

skin_i = s.find('<b:skin>')
skin_j = s.find('</b:skin>')
assert skin_i != -1 and skin_j != -1
css = s[skin_i:skin_j]
spans = css_dead_spans(css, KW_CSS)
assert all(spans[x][1] <= spans[x + 1][0] for x in range(len(spans) - 1))
new_css = ''
last = 0
for a, b in spans:
    new_css += css[last:a]
    last = b
new_css += css[last:]
s = s[:skin_i] + new_css + s[skin_j:]
removed.append('css: %d reglas muertas de Orbit/Clearing/Joyride/Reveal/Tooltips/'
               'Magellan/RefineSlide (~%d chars)' % (len(spans), sum(b - a for a, b in spans)))

# 18c) Verificacion final: ni rastro de los complementos de imagen en todo el theme
for leftover in ['joyride', 'Joyride', 'orbit', 'Orbit', 'clearing', 'Clearing',
                 'reveal-modal', 'magellan', 'tooltip', 'has-tip', 'refineSlide',
                 'RefineSlide', 'imagesLoaded', 'fitVids', 'FitVids', 'Modernizr',
                 'yepnope', 'fluid-width-video', 'pbtthumbimg', 'summary_img',
                 'img_thumb_width', 'img_thumb_height']:
    assert leftover not in s, 'referencia residual a: ' + leftover

# 19) Iconos Font Awesome -> caracteres de texto plano
sub_once(r"<div id='gotoppbt'><h6><i class='fa fa-arrow-up'/></h6></div>",
         "<div id='gotoppbt'><h6>&#8679;</h6></div>",
         'html: boton "subir" sin Font Awesome')
sub_once(r"<div class='sidebar-buttonpbt'><i class='fa fa-plus'/></div>",
         "<div class='sidebar-buttonpbt'><span>+</span></div>",
         'html: boton sidebar sin Font Awesome')

open(DST, 'w', encoding='utf-8').write(s)
print('Escrito:', DST)
print('Elementos retirados/modificados (%d):' % len(removed))
for r in removed:
    print(' -', r)
