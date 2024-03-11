## Rapport de laboratoire 2 - Groupe 2 Équipe 8
### Ines Abdelkefi
### Taha El-Amin Sedjal

## 1. Introduction
Ce rapport présente la mise en œuvre d'un pipeline d'intégration continue (CI) et de la conteneurisation de l'application Oxygène CS dans le cadre du laboratoire 2. L'objectif principal était d'automatiser le processus de construction, de test et de déploiement pour garantir une livraison rapide et fiable du logiciel. Pour s'y faire, nous devions effectuer la modification du code source pour intégrer des variables d'environnement, la sauvegarde des données dans une base de données, et la création d'images Docker optimisées. En outre, des métriques clés ont été sélectionnées pour évaluer les performances du pipeline et garantir une amélioration continue du processus de développement.

## 2. Répartition du Travail
La répartition des tâches a été basée sur nos compétences et préférences individuelles. Bien que nous ayons initialement attribué des responsabilités distinctes, des défis rencontrés nous ont amenés à collaborer étroitement, partageant des connaissances et résolvant des problèmes ensemble.

## 3. Implémentation de la CI
Nous avons opté pour GitLab comme plateforme pour l'implémentation du pipeline CI en raison de sa simplicité d'utilisation et des avantages substantiels qu'il offre. GitLab assure une intégration transparente avec les référentiels Git, offrant un environnement convivial pour la configuration du pipeline.

Cette sélection a été motivée par plusieurs avantages inhérents à l'utilisation de GitLab. Tout d'abord, GitLab propose une intégration complète, regroupant des outils essentiels tels que la gestion du code source, le suivi des problèmes, et la CI/CD au sein d'une seule plateforme. De plus, la CI/CD intégrée simplifie la configuration et l'exécution du pipeline, évitant la nécessité de recourir à des services externes. Enfin, une communauté active, une documentation exhaustive, des forums d'assistance, et des mises à jour fréquentes font de GitLab un choix solide.

## 4. Choix de Métriques CI
Les quatre métriques choisies pour évaluer le pipeline CI ont été sélectionnées en fonction de leur pertinence pour mesurer l'efficacité, la qualité et les performances du processus d'intégration continue. Voici les raisons pour lesquelles ces métriques ont été considérées comme importantes :

### Pipelines Leadtime Avg :

Cette métrique mesure le temps moyen nécessaire pour compléter un pipeline. Elle offre un aperçu du délai d'intégration, permettant d'identifier les goulots d'étranglement et d'améliorer l'efficacité du processus.

### Pipelines Success Rate :

Le taux de réussite des pipelines indique la proportion de pipelines qui se terminent avec succès par rapport au total. Cela permet d'évaluer la fiabilité du pipeline et d'identifier les problèmes fréquents conduisant à des échecs.

### Jobs Leadtime Average :

Mesurer le temps moyen d'exécution des jobs donne une indication plus détaillée sur les étapes individuelles du pipeline. Cela permet de cibler spécifiquement les phases qui prennent le plus de temps, facilitant l'optimisation du processus.

### Jobs Success Rate :

Le taux de réussite des jobs offre une visibilité sur la qualité de chaque étape du pipeline. Identifier les jobs fréquemment en échec aide à concentrer les efforts d'amélioration là où ils sont les plus nécessaires.

## 5. Conclusion
En conclusion, notre objectif initial était de mettre en place un pipeline d'intégration continue (CI) robuste et efficace, accompagné de la conteneurisation Docker de l'application Oxygène CS. À travers l'utilisation de GitLab, nous avons atteint cet objectif avec succès. L'implémentation du pipeline CI, les tests automatisés, la configuration du conteneur Docker, ainsi que l'intégration de métriques pertinentes ont contribué à renforcer notre processus de développement, nous permettant d'assurer une livraison continue de qualité pour l'application Oxygène CS.
