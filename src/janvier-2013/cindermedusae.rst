Cindermedusae - Les Créatures Génératives
=========================================

:date: 2012-12-12
:category: art,informatique
:level: avancé
:author: Marcin Ignac
:translator: Tarek Ziadé


.. note::

   **ARTICLE EN COURS DE TRADUCTION**

.. note::

   Cet article est une traduction adaptée de l'article de Marcin Ignac
   originalement paru en anglais sur son blog à
   `cette addresse <http://marcinignac.com/blog/cindermedusae-making-generative-creatures>`_.

   Vous pouvez retrouvez tous les projets de Marcin ici:
   http://marcinignac.com/projects/category/featured/


.. image:: cindermedusae.jpg
   :alt: Les méduses en action


*Cindermedusae* est un projet qui me tiens beaucoup à cœur. Il a été
réalisé très vite (en une semaine) et a été intensif. Mais les résultats
que j'ai obtenus sont très concluants. J'ai toujours aimé l'idée de
*livre génératif* et la première fois que j'ai entendu parler du concours
de `Written Images <http://writtenimages.net/>`_ ca m'a tout de suite
donné envie de participer.

(EXPLIQUER LE CONCOURS, DIRE QUE C PAS DE LANIME)

----

Je travaillais encore chez `shiftcontrol <http://shiftcontrol.dk>`_ à
cette époque, pour un projet de jeu sous-marin pour la ZDF appelé
`Universum Der Oceane <http://ozeane3d.zdf.de/>`_ en collaboration
avec les architectes de `Hosoya Schaefer <http://www.hosoyaschaefer.com/>`_. Vous
pouvez trouver plus d'information sur ce projet
`ici <http://www.hosoyaschaefer.com/2010/10/universum-der-ozeane-2/>`_.

Nous avions beaucoup de réunions pour discuter de l'ergonomie du jeu et
du comportement des créatures sous-marines - et c'est probablement
ce qui m'a intêressé aux méduses géantes.

Ces animaux sont extraordinaires - j'adore la façon dont elles se
`déplacement lentement <http://vimeo.com/453319>`_.  Un choix parfait
pour tordre des fils de fers avec du code.


Animation procédurale
:::::::::::::::::::::

L'`animation procédurale <https://fr.wikipedia.org/wiki/Animation_proc%C3%A9durale>`_
consiste à animer des objets en temps réel par le biais d'un ensemble de règles
procédurales, c'est-à-dire une description des règles de fonctionnement du
monde physique et un ensemble de conditions initiales.

Ce n'est pas la première fois que je fais de l'animation procédurale.
En fait, toute la `Scène démo <https://fr.wikipedia.org/wiki/Demoscene>`_ en use
et abuse. Un bon exemple est le torus en forme de cactus dans l'introduction de mon
projet `Borntro <http://marcinignac.com/projects/borntro/>`_.

Le code original de *Cindermedusae* est en C++ et utilise la bibliothèque
`Cinder <http://libcinder.org/>`_ mais je décris dans cet article les idées de base
de l'animation de méduses avec des exemples
de code en `processing.js <http://processingjs.org/>`_, le portage de
`Processing <http://processing.org/>`_ en Javascript.

La plupart des exemples sont interactifs et en 2D - c'est plus facile a
comprendre (et a dessiner!). Dans quelques cas je présente des exemples
en 3D et il faut un navigateur compatible `WebGL <https://fr.wikipedia.org/wiki/WebGL>`_
pour que ca fonctionne.

Tête de la méduse
-----------------

Commençons avec un cercle — ou une sphère en 3D, vue du dessus. C'est
l'ensemble des points équidistants d'un point unique, le centre
du cercle. Si ce cercle a pour coordonnées *(0, 0)*, et que
le rayon du cercle est **r**, tous les points du cercles peuvent
être décrits comme les fonction de l'angle **phi**, variant de
0 à 2π

.. code-block:: c++

    x = r * cos(phi)
    y = r * sin(phi)

L'étape suivant consiste à ajuster dynamiquement le rayon avec une
fonction sinusoïdale pour qu'il varie de *0.925* à *1.075* soit
de 92.5% à 107.5% de sa valeure initiale.

On multiplie aussi l'angle par dix pour avoir cet effet de vague
dix fois dans le cercle.

.. code-block:: c++

    x = r * (1 + 0.075 * cos(phi * 10)) * cos(phi)
    y = r * (1 + 0.075 * cos(phi * 10)) * sin(phi)

Les segments rouges que vous voyez sur l'image sont les segments
séléctionnés comme points de départ pour accrocher les tentacules
de la méduse. Nous nous y intéresserons plus tard.


.. image:: medusae_head.jpg
   :alt: Vue des têtes du dessus - cliquez pour le code
   :scale: 50
   :target: http://marcinignac.com/blog/cindermedusae-making-generative-creatures/mesh01.html


Si l'on regarde la tête de notre méduse en 2D sur le côté, c'est aussi
un cercle, puisqu'à la fin nous jouons avec des sphères.

La différence avec le calcul précédent est que cette fois-ci, la
variation de l'angle *theta* va de 0 (en haut) à 2π (en bas)

(POURQUOI ON PASSE DE PHI A THETA?)

La tête est symétrique le long de l'axe Y, donc nous construirons 2 points
à chaque étape - un à gauche et un à droite:

::

    x = r * cos(theta)
    y = r * sin(theta)
    x' = -x
    y' =  y

Sachant que la tête de la méduse ressemble plus à un dôme qu'une sphère,
nous devons faire une forme qui est convexe au dessus et concave en dessous.

Il suffit d'inverser la valeur de la coordonnée Y en atteignant π/2, ou
90' dans notre cas. On ajoute aussi *r/2* pour pousser l'arc de cercle
obtenu après π/2 vers le bas, afin que les deux arcs ne se confondent pas:

.. code-block:: c++

    if (theta < PI/2) {
        x = r * cos(theta) y = r * sin(theta)
    } else {
        x = r * cos(theta)
        y = -r * sin(theta) + r * 0.5
    }

Enfin, on arrondi les angles pour un meilleur rendu, et aussi pour éviter
des artefacts d'ombre. Je ne vais pas décrire cette étape ici, car
c'est juste un *if* et un *sin* supplémentaires. Vous pouvez lire le
code source fourni.

.. image:: medusae_head2.jpg
   :alt: Vue des têtes de côté  - cliquez pour le code
   :scale: 50
   :target: http://marcinignac.com/blog/cindermedusae-making-generative-creatures/mesh02.html

----

Il y a de meilleures techniques d'animations mais comme *Written Images*
n'était pas un concours d'animation, j'ai utilisé l'outil le plus simple:
*sin()*. Personne ne verra la différence sur des pages statiques de
toute façon.

Pour chaque frame ou je calcul les positions x et y, je calcul aussi
`la droite normale à la surface <https://fr.wikipedia.org/wiki/Normale_%C3%A0_une_surface>`_.

Ensuite, si l'animation est lancée, je déplace le point le long de la normale
en utilisant la valeur de la fonction *sin()* à un instant *t*.
Cette formule déplace les points mais sans rien faire de plus, la tête
se mettrait à faire des pulsations comme un cœur, en grossissant et
rétrécissant - car tous les points se déplacent.

C'est pourquoi j'ajoute *y \* 0.5* à *t* pour introduire un *phase shift*
(TRADUIRE) le long de l'axe Y et la structure en fil de fer (*wireframe* ou
*mesh* en anglais) commence à bouger d'une manière un peu plus naturelle.

.. code-block:: c++

    x += normal.x * sin(t + y * 0.5)
    y += normal.y * sin(t + y * 0.5)


.. image:: medusae_head3.jpg
   :alt: Vue animée des têtes de côté - cliquez pour code & animation
   :scale: 50
   :target: http://marcinignac.com/blog/cindermedusae-making-generative-creatures/mesh03.html


J'ai décidé de combiner toutes les étapes dans un script processing.js en 3D,
et à ma surprise le code obtenu est quasiment un copier-coller de la version C++.
J'ai essayé de garder le code le plus simple & clair possible pour cet article,
donc il n'est pas optimal: les performances ne sont pas au rendez-vous.

.. image:: medusae_head4.jpg
   :alt: Vue animée en 3D - cliquez pour code & animation
   :scale: 50
   :target: http://marcinignac.com/blog/cindermedusae-making-generative-creatures/mesh04.html


Tentacules
----------

**Problème** Etant donné une courbe - ou plutôt une ligne polygonale, fabriquez un
mesh en forme de tube autour de cette ligne.

**Solution** On démarre avec trois vecteurs perpendiculaires:

- **Forward** - le vecteur sur la droite normale à l'endroit où je veux accrocher
  la tentacule - or if we have curve formula it would be the tangent vector

- **Up**  - choisi arbitrairement : *(0,1,0)* et

- **Left** qui peut être calculé avec `la règle de la main
  droite <https://fr.wikipedia.org/wiki/Regle_de_la_main_droite>`_.

La formule de la la règle de la main droite s'applique ainsi::

    L = U x F

Où *x* est le `produit vectoriel <https://fr.wikipedia.org/wiki/Produit_vectoriel>`_
des deux vecteurs à trois dimensions.

Pour le deuxième point de notre ligne, on a le nouveau vecteur
**F'** et l'on conserve le même vecteur **L**, on peut calculer le
nouveau vecteur **U'**::

    U' = F' x L

En répétant cette opération pour chaque point/segment de la ligne,
on obtient une série de coordonnées pour chaque vecteur
*Up*, *Front* et *Left*.


.. image:: right_hand_rule.jpg
   :scale: 50
   :alt: Règle de la main droite

Tous ces calculs sont inspirés du `repère
de Frenet <https://fr.wikipedia.org/wiki/Rep%C3%A8re_de_Frenet>`_.

Si vous développez dans Cinder, vous n'avez pas à vous soucier de
tous ces calculs, car le développeur `Chaoticbob
<http://forum.libcinder.org/#User/chaoticbob>`_ a contribué
un système encore plus performant: les `Parallel Transport Frames
<http://forum.libcinder.org/#topic/23286000000494005>`_.

Maintenant que nous avons les vecteurs *Up* et *Forward*, il est
facile de construire des triangles. Dans l'exemple suivant j'ai
ajouté deux élements supplémentaires. Le premier ajout
est une réduction du vecteur *Up* pour que la pointe de la tentacule
apparaisse plus fine.

Le deuxième ajout est un enroulement de la
tentacule en fonction de la position de la souris.
La tentacule est de plus en plus enroulée au fur et à mesure que l'on
se rapproche de la pointe - la force de cette enroulement est
représentée par des lignes rouges.


.. image:: medusae_tentacle.jpg
   :alt: Tentacules animées - cliquez sur l'image
   :scale: 50
   :target: http://marcinignac.com/blog/cindermedusae-making-generative-creatures/mesh05.html

Nous sommes maintenant prêts à attacher les tentacules à la tête.
Je regroupe tous les éléments car le travail des ombres masquera les
discontinuités de la surface.


.. image:: heads_tentacle.jpg
   :alt: Tentacules & corps animés - cliquez sur l'image
   :scale: 50
   :target: http://marcinignac.com/blog/cindermedusae-making-generative-creatures/mesh06.html


Géométrie finale
----------------

The geometry I used for renders is much higher density mostly to have nice
smooth curves and avoid antialiasing artifacts.

.. image:: mesh.jpg
   :alt: Rendu final


Procedural shading
::::::::::::::::::


When I started I was aiming for very natural look so I was experimenting with
Subsurface Scattering and even managed to get some decent looking results. I
changed my mind after stumbling upon works by Ernst Haeckel and his amazing
book "Kunstformen der Natur" - I knew that this is the way to go.

First step is to use standard diffuse lighting just to see if my mesh is smooth
enough and I don't have any strange behaving normals

.. image:: diffuse.jpg
   :alt: Ombres


Hatching
::::::::


There are many research papers on how to achieve sketchy look in realtime. I
based my implementation on code from OpenGL Shading Language Book. The
algorithm first generate vertical stripes along texture coordinates and then
chooses the stripe density based on diffuse lighting. The less light the more
dense the black stripes are. One important aspect was to choose the the right
width of the stripes so to output is visually interesting but we don't get too
much Moiré effect. Big offscreen FBO (4080 × 2720 px) and antialiasing helps a
lot.

.. image:: hatching.jpg
   :alt: Hatching - cliquez pour la version hi-res
   :target: http://marcinignac.com/blog/cindermedusae-making-generative-creatures/hatching_hi.jpg


Unfortunately There will be no ProcessingJS examples in this part because some
features depends on WebGL GLSL extensions like GL_OES_standard_derivatives and
dFdx / dFdy functions that are not supported by any WebGL implementation I know
yet. Copy pasting source code also doesn't make sense so please refer to the
book if interested.


Colors
::::::

Every image is composited out of 5 layers:

yellow background color orange page corders dirt black sketchy hatch blue
highlights and pink borders

Both orange page corners and blue highlights are masked by noise so they look
like drawn using crayons.

.. image:: color_layers.jpg
   :alt: Colorisation - cliquez pour la version hi-res
   :target: http://marcinignac.com/blog/cindermedusae-making-generative-creatures/color_layers_hi.jpg


.. image:: medusae_final.jpg
   :alt: Résultat final combiné


Paramétrage
:::::::::::

Very important thing to mention is that all the parameters are exposed through
simple GUI system I developed. This allows my to play with them and see how
shape of the creature changes and what should be minimal and maximum values
that makes sense. Having that I can simply choose a random value for each
variable and be sure every jellyfish will look ok.


.. image:: gui.jpg
   :alt: Interface de paramétrage



La suite ?
::::::::::

I want to work more on this project. First obvious step would be to optimize it
so it runs on a decent framerate when animated. Right now it's around 10fps. I
was thinkning about making WebGL port so people can create their own creatures
online. The plan is also to extend the system and play with different organism
types or plants.
