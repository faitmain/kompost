## -*- coding: utf-8 -*-

<!DOCTYPE html>
<html lang="en"><head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <meta charset="utf-8">
    <title>${title}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Vulgarisation pour Geeks">
    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->
    <link href="/media/bootstrap.css" rel="stylesheet">
    <link href="/media/bootstrap-responsive.css" rel="stylesheet">
    <link href="/media/bootswatch.css" rel="stylesheet">
    <link rel="shortcut icon" href="http://faitmain.org/favicon.ico" />
</head>

  <body class="preview" data-spy="scroll" data-target=".subnav" data-offset="80">

    <div class="container">

<header class="jumbotron subhead" id="overview">
  <div class="row">
    <div class="span6">
      <a href="/"><h1>Fait Main</h1></a>
      <p class="lead">Electronique | Informatique | Art | Bouffe | Ecologie</p>
    </div>
  </div>
  <%block name="header"/>
</header>


<h1>${title}</h1>

${body}


<br><br><br><br>

      <hr/>


  <footer id="footer">
    <%block name="footer">
        <p class="pull-right"><a href="#"><img src="/media/up.png"></a></p>
        <div class="links">
          Contenu en licence <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-By-SA</a> ·
          <a href="https://twitter.com/faitmain">Twitter</a> ·
          <a href="https://github.com/faitmain">GitHub</a> ·
        Thème <a target="_blank" href="http://twitter.github.com/bootstrap/">Bootstrap</a> par <a target="_blank" href="http://thomaspark.me/">Thomas Park</a> avec quelques retouches ·
        <a target="_blank" href="http://glyphicons.com/">Icones</a> · <a target="_blank" href="http://www.google.com/webfonts">Google WebFonts</a>
        </div>
      </%block>
      </footer>

    </div>

    </div><!-- /container -->


    <script src="/media/jquery.js"></script>
    <script src="/media/bootstrap.js"></script>
    <script src="/media/application.js"></script>
    <script src="/media/bootswatch.js"></script>
</body></html>
