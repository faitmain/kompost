## -*- coding: utf-8 -*-

<!DOCTYPE html>
<html lang="en"><head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <meta charset="utf-8">
    <title>${title} - Fait Main Magazine</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Vulgarisation pour Geeks">
    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->
    <link href="http://cnd.faitmain.org/media/bootstrap.css" rel="stylesheet">
    <link href="http://cnd.faitmain.org/media/bootstrap-responsive.css" rel="stylesheet">
    <link href="http://cnd.faitmain.org/media/bootswatch.css" rel="stylesheet">
    <link href="http://cnd.faitmain.org/media/pygments_style.css" rel="stylesheet">
    <link rel="shortcut icon" href="http://cnd.faitmain.org/favicon.ico" />
</head>

  <body class="preview" data-spy="scroll" data-target=".subnav" data-offset="80">
<div class="navbar navbar-fixed-top">

<div class="navbar-inner">
<div class="container branding">
<a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
<span class="icon-bar"></span>
<span class="icon-bar"></span>
<span class="icon-bar"></span>
</a>
<a class="brand" href="/">Fait Main</a>
<div class="nav-collapse">
<ul class="nav">
<li><a href="/electronique.html" title="A propos">Electronique</a></li>
<li><a href="/informatique.html" title="Informatique">Informatique</a></li>
<li><a href="/art.html" title="Art">Art</a></li>
<li><a href="/cuisine.html" title="Cuisine">Cuisine</a></li>
<li><a href="/ecologie.html" title="Ecologie">Ecologie</a></li>
<li><a target="_blank" title="Twitter" href="http://twitter.com/FaitMainMag" id="toptwitter" rel="nofollow"><img src="http://cnd.faitmain.org/media/twitter.png"/></a></li>
<li><a target="_blank" href="https://plus.google.com/+faitmainmag/posts" id="topgoogleplus" rel="nofollow"><img src="http://cnd.faitmain.org/media/google_plus.png"/></a> </li>
<li><a target="_blank" title="RSS" href="/rss" id="toprss"><img src="http://cnd.faitmain.org/media/rss.png"/></a></li>
<li><a target="_blank" title="RSS" href="http://github.com/tarekziade/faitmain" id="topgithub"><img src="http://cnd.faitmain.org/media/github.png"/></a></li>
</ul>
</div><!--/.nav-collapse -->
</div>

</div>
</div>


    <div class="container">

<header class="jumbotron subhead" id="overview">
  <div class="row">
    <div class="span9">
      <a href="/"><h1>Fait Main</h1></a>
      <p class="lead">Electronique ∝ Informatique ∝ Art ∝ Bouffe ∝ Ecologie</p>
    </div>
  </div>
  <%block name="header"/>
</header>


<div class="alert alert-error">
Attention le magazine n'est pas encore officiellement lancé. Ceci est un prototype. Ne pas diffuser.
</div>

<h1>${title}</h1>

%if paths:
 <p>Tous les articles sur ce sujet:</p>
  <ul>
   %for path, title_ in paths:
    <li><a href="${path}">${title_}</a></li>
   %endfor
  </ul>
%else:
  <p>Aucun article sur ce sujet pour le moment.</p>
%endif


<br/><br/>
 <p class="pull-right"><a href="#"><img src="http://cnd.faitmain.org/media/up.png"></a></p>

  <footer id="footer">
  <div class="inner">
    <%block name="footer">
    <div class="links">
      <ul>
        <li>© 2012 FaitMain</li>
        <li><a href="/apropos.html">A propos</a></li>
        <li>Contenu <a href="https://creativecommons.org/licenses/by-nc-sa/2.0/">CC-By-NC-SA</a></li>
      </ul>
      <div style="clear:both"/>
     </div>
    </%block>
  </div>
  </footer>
 </div>
    <script async src="http://cnd.faitmain.org/media/jquery.js"></script>
    <script async src="http://cnd.faitmain.org/media/bootstrap.js"></script>
    <script src="http://cnd.faitmain.org/media/retina.js"></script>
</body></html>

