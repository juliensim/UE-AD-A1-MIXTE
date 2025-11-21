# Booking API

API GraphQL permettant de consulter et gérer des réservations.

L’accès est sécurisé via un header `X-Token` validé auprès de l’API User.

Port utilisé : 3002

---

## Authentification et permissions

Toutes les requêtes doivent inclure le header **X-Token**. C'est une clé d'accès personnelle pour chaque utilisateur.

On vérifie :
- la validité du token (qu'un utilisateur correspond)
- le **niveau de permission** (`user` ou `admin`) si un niveau de permission doit être vérifié


# Schémas GraphQL

## Types

### Booking
```graphql
type Booking {
  userid: String!
  dates: [BookingDate!]!
}
```

### BookingDate
```graphql
type BookingDate {
  date: String!
  movies: [String!]!
}
```

### Movie
```graphql
type Movie {
  id: String!
  title: String
  rating: Float
  director: String
  actors: [Actor!]
}
```

### Actor
```graphql
type Actor {
  id: String!
  name: String!
  films: [String!]
}
```

### BookingDetails (réponse enrichie)
```graphql
type BookingDetails {
  userid: String!
  movies: [Movie!]!
}
```

### AddBookingInput
```graphql
input AddBookingInput {
  new_userid: String!
  new_dates: [AddDateInput!]!
}
```

### AddDateInput
```graphql
input AddBookingDateInput {
  new_date: String!
  new_movies: [String!]!
}
```

## **booking_by_userid**(userid: String!): Booking
**Permission requise : `user`**

Permet de récupérer les réservations associées à un utilisateur.

### Exemple
```graphql
query {
  booking_by_userid(_userid: "user42") {
    userid
    dates {
      date
      movies
    }
  }
}
```

## **all_bookings**: [Booking]
**Permission requise : `admin`**

Retourne toutes les réservations.

### Exemple
```graphql
query {
  all_bookings {
    userid
    dates {
      date
      movies
    }
  }
}
```


## **booking_details**(userid: String!): BookingDetails
**Permission requise : `user`**

Retourne les informations enrichies :
- films correspondants aux movies réservés
- acteurs associés

### Exemple
```graphql
query {
  booking_details(_userid: "user42") {
    userid
    movies {
      id
      title
      actors {
        name
      }
    }
  }
}
```

## **add_booking**(userid: String!, new_booking: AddBookingInput!): Booking
**Permission requise : `user`**

Ajoute une nouvelle réservation pour un utilisateur.

### Exemple
```graphql
mutation {
  add_booking(
    _userid: "user42",
    _new_booking: {
      new_userid: "user42",
      new_dates: [
        { new_date: "2025-02-01", new_movies: ["m01", "m02"] }
      ]
    }
  ) {
    userid
    dates {
      date
      movies
    }
  }
}
```

---

## **delete_booking**(userid: String!): String
**Permission requise : `user`**

Supprime les réservations pour un utilisateur donné.

Retourne un message de confirmation :
```
"user42 - deleted 3 bookings"
```

### Exemple
```graphql
mutation {
  delete_booking(_userid: "user42")
}
```

---


# Récapitulatif des permissions

| Resolver          | Permission |
|------------------|------------|
| booking_by_userid | user |
| booking_details   | user |
| all_bookings      | admin |
| add_booking       | user |
| delete_booking    | user |

---

# Dépendances externes

L’API interagit avec :
- **User** : validation du token et des permissions, détails de réservation
- **Movie** : détails de réservation
- **Schedule** : vérifier qu'une séance correspond avant d'ajouter une réservation