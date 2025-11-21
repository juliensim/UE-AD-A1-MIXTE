# Schedule API

Le service gRPC Schedule permet de gérer un planning de films stocké en MongoDB.  
Il expose plusieurs méthodes permettant :

- d’obtenir les films programmés à une date donnée  
- d’obtenir les dates où un film est programmé  
- d’ajouter une programmation  
- de supprimer une programmation

Port utilisé : 3003

## Authentification et permissions

Toutes les requêtes doivent inclure le header **X-Token**. C'est une clé d'accès personnelle pour chaque utilisateur.

On vérifie :
- la validité du token (qu'un utilisateur correspond)
- le **niveau de permission** (`user` ou `admin`) si un niveau de permission doit être vérifié


## Méthodes de l’API

### GetMoviesByDate

Retourne les films programmés pour la date donnée.  
Permission requise : **user**

Requête :
```json
{
  "date": "2024-05-01"
}
```

Réponse :
```json
{
  "moviesid": [
    {"id": "MOV123"},
    {"id": "MOV456"}
  ]
}
```

---

### GetDatesForMovie

Retourne les dates où un film est programmé.  
Permission requise : **user**

Requête :
```json
{
  "id": "MOV123"
}
```

Réponse :
```json
{
  "dates": [
    {"date": "2024-05-01"},
    {"date": "2024-05-02"}
  ]
}
```

---

### AddSchedule

Ajoute des films pour une date (ou crée la date).  
Permission requise : **admin**

Requête :
```json
{
  "date": "2024-06-10",
  "movies": ["MOV777", "MOV888"]
}
```

Réponse : identique à la requête.

---

### DeleteSchedule

Supprime une liste de films pour une date.  
Si la date n’a plus de films, elle est supprimée.  
Permission requise : **admin**

Requête :
```json
{
  "date": "2024-06-10",
  "movies": ["MOV777"]
}
```

Réponse : identique à la requête.

---