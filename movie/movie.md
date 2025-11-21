# Movie API

API GraphQL permettant de consulter, ajouter, mettre à jour et supprimer
des films.

L’accès est sécurisé via un header `X-Token` validé auprès de l’API User.

Port utilisé : 3001

## Authentification et permissions

Toutes les requêtes doivent inclure le header **X-Token**. C'est une clé d'accès personnelle pour chaque utilisateur.

On vérifie :
- la validité du token (qu'un utilisateur correspond)
- le **niveau de permission** (`user` ou `admin`) si un niveau de permission doit être vérifié


# Schémas GraphQL

## Types

### Movie

``` graphql
type Movie {
  id: String!
  title: String
  rating: Float
  director: String
  actors: [Actor!]
}
```

### Actor

``` graphql
type Actor {
  id: String!
  name: String!
  films: [String!]
}
```

---

## **movie_with_id**(\_id: String!): Movie

**Permission requise : `user`**

Récupère un film via son identifiant.

### Exemple

``` graphql
query {
  movie_with_id(_id: "m01") {
    id
    title
    rating
    actors {
      name
    }
  }
}
```

## **movie_by_title**(\_title: String!): Movie

**Permission requise : `user`**

Récupère un film via son titre exact.

### Exemple

``` graphql
query {
  movie_by_title(_title: "Inception") {
    id
    title
    rating
  }
}
```

## **all_movies**: [Movie](#movie)

**Permission requise : `user`**

Retourne tous les films présents dans la base.

### Exemple

``` graphql
query {
  all_movies {
    id
    title
    rating
  }
}
```

## **add_movie**(\_id: String!, \_title: String!, \_rate: Float!, \_director: String!): Movie

**Permission requise : `admin`**

Ajoute un nouveau film s'il n'existe pas déjà.

Retourne `null` si un film avec le même ID existe déjà.

### Exemple

``` graphql
mutation {
  add_movie(
    _id: "m99",
    _title: "New Movie",
    _rate: 4.5,
    _director: "John Doe"
  ) {
    id
    title
  }
}
```

## **update_movie_rate**(\_id: String!, \_rate: Float!): Movie

**Permission requise : `admin`**

Met à jour la note d'un film.

Retourne `null` si aucun film n'existe avec cet ID.

### Exemple

``` graphql
mutation {
  update_movie_rate(
    _id: "m01",
    _rate: 4.9
  ) {
    id
    title
    rating
  }
}
```

## **delete_movie**(\_id: String!): Movie

**Permission requise : `admin`**

Supprime un film et retourne les données supprimées.\
Retourne `null` si aucun film n'existe.

### Exemple

``` graphql
mutation {
  delete_movie(_id: "m01") {
    id
    title
  }
}
```

---

# Récapitulatif des permissions

  Resolver            Type       Permission
  ------------------- ---------- ------------
  movie_with_id       Query      user
  movie_by_title      Query      user
  all_movies          Query      user
  add_movie           Mutation   admin
  update_movie_rate   Mutation   admin
  delete_movie        Mutation   admin

---

# Dépendances externes

L'API interagit avec :

-   **User** : validation du token et permissions
