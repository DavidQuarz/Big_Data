{
  "swagger" : "2.0",
  "host" : "traffic.api.iledefrance-mobilites.fr",
  "basePath" : "/v1/tr-unitaire",
  "schemes" : [ "https" ],
  "paths" : {
    "/stop-monitoring" : {
      "get" : {
        "description" : "Horaires estimés des prochains passages aux arrêts. \n\nActuellement, les horaires de prochains passages à un arrêt en temps réel ne sont disponibles que pour une partie du réseau d’Ile-de-France. L’ensemble des arrêts du réseau seront progressivement disponibles.\n\nLe Jeu de données Périmètre des données temps réel disponibles expose la liste des arrêts par ligne/ transporteurs concernés par ce service.\n\nLes requêtes et réponses sont exprimées au format SIRI Lite, vous trouverez plus d’informations sur ce format d’échange de données dans la documentation technique.\n\nPoint d'entrée pour récupérer les informations de type \"Passage\"\n",
        "operationId" : "getPassages",
        "produces" : [ "application/json" ],
        "parameters" : [ {
          "description" : "Stop Point ID (exemple : \"STIF:StopPoint:Q:22388:\" Chaussée d'Antin La Fayette))",
          "required" : true,
          "in" : "query",
          "name" : "MonitoringRef",
          "type" : "string"
        } ],
        "responses" : {
          "200" : {
            "description" : "OK",
            "schema" : {
              "$ref" : "#/definitions/StopMonitoringResponseDelivery"
            }
          },
          "400" : {
            "description" : "BAD Request : La requête contient des identifiants qui sont inconnus"
          },
          "500" : {
            "description" : "Internal Server Error"
          },
          "503" : {
            "description" : "Service Unavailable"
          }
        }
      }
    }
  },
  "definitions" : {
    "StopMonitoringResponseDelivery" : {
      "properties" : { },
      "type" : "object"
    }
  },
  "securityDefinitions" : {
    "OAuthImplicit" : {
      "type" : "oauth2",
      "description" : "OAuth",
      "flow" : "implicit",
      "scopes" : {
        "read-data" : ""
      },
      "authorizationUrl" : "https://as.api.iledefrance-mobilites.fr/api/oauth/authorize",
      "x-axway" : {
        "typeDisplayName" : "OAuth 2.0",
        "scopesMatching" : "Any",
        "accessTokenLocation" : "HEADER",
        "accessTokenLocationQueryString" : "",
        "authorizationHeaderPrefix" : "Bearer",
        "tokenName" : "access_token"
      }
    },
    "OAuthAccessCode" : {
      "type" : "oauth2",
      "description" : "OAuth",
      "flow" : "accessCode",
      "scopes" : {
        "read-data" : ""
      },
      "authorizationUrl" : "https://as.api.iledefrance-mobilites.fr/api/oauth/authorize",
      "tokenUrl" : "https://as.api.iledefrance-mobilites.fr/api/oauth/token",
      "x-axway" : {
        "typeDisplayName" : "OAuth 2.0",
        "scopesMatching" : "Any",
        "accessTokenLocation" : "HEADER",
        "accessTokenLocationQueryString" : "",
        "authorizationHeaderPrefix" : "Bearer",
        "clientIdName" : "client_id",
        "clientSecretName" : "client_secret",
        "tokenName" : "access_code"
      }
    }
  },
  "security" : [ {
    "OAuthImplicit" : [ "read-data" ]
  }, {
    "OAuthAccessCode" : [ "read-data" ]
  } ],
  "info" : {
    "title" : "Prochains passages (plateforme Île-de-France Mobilités)",
    "description" : "Horaires estimés des prochains passages aux arrêts.\n\nActuellement, les horaires de prochains passages à un arrêt en temps réel ne sont disponibles que pour une partie du réseau d’Ile-de-France. L’ensemble des arrêts du réseau seront progressivement disponibles.\n\nLe Jeu de données [Périmètre des données temps réel disponibles sur la plateforme d'échanges Île-de-France Mobilités](https://data.iledefrance-mobilites.fr/explore/dataset/perimetre-tr-plateforme-stif/information/) expose la liste des arrêts par ligne/ transporteurs concernés par ce service.\n\nLes requêtes et réponses sont exprimées au format SIRI Lite, vous trouverez plus d’informations sur ce format d’échange de données dans la documentation technique.\n\n----------\n\n**Points d’entrée sur l’API**\n\nLes points d'entrée implémentés permettent de simplifier l'utilisation de l'API en répondant aux principaux cas d'usages.\n\n`GET` /stop-monitoring/{MonitoringRef}\n\n----------\n\n**Accès à l'API**\n\nVous devez être connecté à [votre compte utilisateur](https://portal.api.iledefrance-mobilites.fr/fr/sign-in-fr) pour accéder à l'API.\n\nVous avez également la possibilité d'ouvrir votre accès à des applications tierces. Vous devez pour cela utiliser une clé d'API, obtenue [via le portail de votre compte](https://opendata.stif.info/account) (Rubrique \"Mes Clés d'API\" -> \"Générer une clé d'authentification\"). Plus d'informations dans la documentation générale.\n\n----------\n**Documentation générale**\n\n[Une documentation générale](https://portal.api.iledefrance-mobilites.fr/images/com_apiportal/doc/IDFM-portailAPI-documentation.pdf) permet de mieux appréhender l’API et d’en connaître les précautions d'usage.\n\n----------\n\n**Conditions Générales d'Utilisation de l'API et licence des données**\n\nL'utilisation de l'API Île-de-France Mobilités est soumise à des [Conditions Générales d'Utilisation](https://portal.api.iledefrance-mobilites.fr/fr/cgu) Les données issues de l'API Île-de-France Mobilités sont soumises à la licence [Open Database License (OdBL)](https://spdx.org/licenses/ODbL-1.0.html#licenseText)\n",
    "version" : "1.0.0"
  },
  "x-axway" : {
    "corsEnabled" : true,
    "basePaths" : [ "" ],
    "serviceType" : "rest",
    "deprecated" : false,
    "tags" : {
      "Temps réel - real time" : [ "source plateforme Île-de-France Mobilités" ]
    },
    "image" : "/api/portal/v1.3/discovery/swagger/apis/6289071e-1d0b-42b8-b2c4-08ea6411d048/image",
    "availableSDK" : {
      "ios-swift" : "/discovery/sdk/6289071e-1d0b-42b8-b2c4-08ea6411d048/ios-swift",
      "titanium" : "/discovery/sdk/6289071e-1d0b-42b8-b2c4-08ea6411d048/titanium",
      "android" : "/discovery/sdk/6289071e-1d0b-42b8-b2c4-08ea6411d048/android",
      "nodejs" : "/discovery/sdk/6289071e-1d0b-42b8-b2c4-08ea6411d048/nodejs"
    }
  }
}