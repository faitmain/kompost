## -*- coding: utf-8 -*-

<!DOCTYPE html>
<html lang="en"><head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <meta charset="utf-8">
    <title>Fait Main</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Vulgarisation pour Geeks">
    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->
    <link href="http://cnd.faitmain.org/media/bootstrap.css" rel="stylesheet">
    <link href="http://cnd.faitmain.org/media/bootstrap-responsive.css" rel="stylesheet">
    <link href="http://cnd.faitmain.org/media/bootswatch.css" rel="stylesheet"> 
    <link rel="shortcut icon" href="http://cnd.faitmain.org/favicon.ico" />
    <%block name="head"/>
</head>

  <body class="preview" data-spy="scroll" data-target=".subnav" data-offset="80">

    <div class="container">

<header class="jumbotron subhead" id="overview">
  <div class="row">
    <div class="span6">
      <a href="/"><h1>Fait Main</h1></a>
      <p class="lead">Electronique ∝ Informatique ∝ Art ∝ Bouffe ∝ Ecologie</p>
    </div>
  </div>
  <%block name="header"/>
</header>


${self.body()}

<div class="span11 center">
<span id="EOD">§</span>
</div>
<br/><br/>

  <footer id="footer">
    <%block name="footer">
    <div class="links">
      <ul>
        <li>Contenu <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-By-SA</a></li>
        <li><a href="https://twitter.com/faitmain">Twitter</a></li>
        <li><a href="https://github.com/faitmain">GitHub</a></li>
        <li><p>Design adapté de <a target="_blank" href="http://thomaspark.me/">Thomas Park</a></p></li>
        <li><a target="_blank" href="http://glyphicons.com/">Icones</a><li>
         <li><a target="_blank" href="http://www.google.com/webfonts">Polices</a></li>
      </ul>
      <div style="clear:both"/>
     </div>
     <p class="pull-right"><a href="#"><img src="http://cnd.faitmain.org/media/up.png"></a></p>
    </%block>
  </footer>
 </div>
    <script src="http://cnd.faitmain.org/media/jquery.js"></script>
    <script src="http://cnd.faitmain.org/media/bootstrap.js"></script>
    <script src="http://cnd.faitmain.org/media/retina.js"></script>
</body></html>
