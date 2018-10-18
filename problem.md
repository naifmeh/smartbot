# Avoiding bot detection through reinforcement learning

## Definition du problème :

Nous désirons que notre agent parvienne a éviter la détection et le blocage de notre bot a travers les sites web specifiés. Les algorithmes de détection sont connus au préalable et seront utilisés afin de determiner les stratégies de contournement.
Nous utiliserons le reinforcement learning afin de résoudre le problème.

## Modèlisation du problème en terme de reinforcement learning

Dans le cadre de notre problème, il convient de modeliser notre environnement et le contexte afin d'être le plus proche de la réalité.

* **But** : Eviter la détection du bot par les systèmes de détection présents.

* **Agent** : Dans notre cas, un controlleur externe est plus approprié en raison du fait que la tache du bot doit correspondre uniquement à celle prédefinie. Nous devons également pouvoir dimensionner la solution à plusieurs bots.

* **Environnement** : Le bot, controllé par l'agent, et son environnement, soit, le web ?

* **Action** :
    * Changement d'adresse IP
    * Varier le nombre de requêtes dans un même site web
    * Variation des mouvements de la souris et keystrokes
    * Variation de la durée de la session
    * Varier les headers HTTP
    * Varier le pourcentage d'images et de documents récupérés 
    * Varier le taux de requêtes HTTP séquentielles.
    * Varier l'user agent
    * Varier la liste des plugins
    * Une action pour éviter de cliquer sur les liens cachés ?
    * Varier le delai de navigation entre deux pages
    * Varier les proxys IP
    * > On met en place une lookup table avec la combinaison de toutes les configurations + 1 (ne rien changer), et on leur assigne une proba qui sera déterminée par l'algorithme.
    On aura 12!+1 = 479.001.601 combinaisons possibles cependants.
    

* **Etats** : 
    * Possibilité de définir les états par les sites web à visiter.
    * Possibilité de définir les états sur les hyperliens visités dans un même site web.
    * Etat terminal : soit le bot est bloqué, soit nous avons parcours la liste des sites web à visiter.
    * > Le mieux, c'est un nombre fixé de sites a visiter, chaque site est un état : le comportement de notre bot pour chaque site ne varie pas, donc on peut les considérer comme des états. 

* **Gains** : (A dévelloper)
    * 0 Dans le cas d'un site crawlé sans détection. (pourquoi 0 ? car le taux de non-detection sera surement élevé, on ne prendre donc rarement en compte les gains négatifs. Solution : discounting factor)
    * -1 Dans le cas de détection.
    * > 0 Si un site est crawlé sans detection, +1 si on finit tout le batch sans detection, -1 si on est détectés. **Les gains sont a revoir, peuvent être trop élevés.**

* **Policies** :
    * Définies par notre algorithme dans le cas de l'utilisation des policy gradient methods.
    * Sinon, on cherche a minimiser la détection, donc optimiser les paramètres permettants de ne pas se faire détection.
    * > Choisir la meilleure configuration pour éviter la détection.

**Questions** : 

- Dois-t-on entraîner notre algorithme sur des épisodes, ou en continu ?
> Je tend plutôt pour un apprentissage continu, soit, l'utilisation d'algorithmes on-line. Mais un épisode continu est possible, en considérant chaque site comme un épisode, et les états seront ainsi les liens cliqués, les documents récupérés, etc...

- Doit-on utiliser des fonctions d'approximation pour approximer les state-values ?

> Ça induirait une discretisation des états. Nos états ne sont pas discrétisables en features, donc je doute que l'on puisse utiliser des fonctions d'approximation.

- Quels sont les meilleurs algorithmes dans notre cas ?

> Après une première révision du problème, je tend plutôt pour le policy gradient methods, qui permet de determiner la policy idéale afin de sélection l'action idéale sans avoir à consuler la state-value.

- Dois-t-on partir sur un algorithme one-step ou n-steps ?

> Il est préférable d'utiliser un algorithme n-step afin d'éviter une mise à jour des paramètres qu'en fin d'épisode. 

- Dois-t-on diminuer les retours à chaque étape ?

> Oui, si on considère un épisode comme le parcours d'une série de site web.

- Est-il préférable d'utiliser un algorithme fonctionnant off-policy ou on-policy ?

> Il vaut mieux un algorithme off-policy afin d'améliorer notre policy.

**Quels sont les possibles algorithmes suites aux réponses précédentes ?**

* Actor-critic with eligibility traces : ELigibility traces nous permet d'introduire une mémoire à court terme, permettant de prendre en compte les résultats des états précédents. 
Permet de determiner la policy.

* REINFORCE with baseline.

* Q(y), Expected Sarsa(y), Tree backup(y)

* Semi-gradient TD(y)

## Update

What about a double RL program ?
RL choice which states would simply be pick website, pick action or etc, then if we pick website, all new kind of actions for
different states

## Update 2

Représenter les etats par la config du bot
Claquer un reward pour un certain objectif atteint