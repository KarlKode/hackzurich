hackzurich - GetCooking
=======================

Formats
-------

.h3 Ingredient

```json
{
  "ingredient": {
    "ean": 6,
    "id": 10,
    "image": "//migros-cache.fsi-viewer.com/fsicache/server?type=image&source=images%2Fmigros_api%2Fstaging%2Fproduct_153930500000.jpg&renderer=original",
    "title": "SE M-CLAS MAISKOER. 6X285DS"
  }
}
```

.h3 Recipe

```json
{
  "recipe": {
    "difficulty": 1,
    "duration": 30,
    "id": 1,
    "images": null,
    "ingredients": [
      {
        "ean": 123,
        "id": 1,
        "image": null,
        "title": "tomato"
      },
      {
        "ean": 124,
        "id": 2,
        "image": null,
        "title": "onion"
      }
    ],
    "missing": 0,
    "steps": [],
    "title": "tomato soup"
  }
}
```

.h3 Shopping List
```json
{
  "ingredients": [
    {
      "ean": 3086120017446,
      "id": 4,
      "image": null,
      "title": "markers"
    }
  ]
}
```

.h3 Inventory
```json
{
  "inventory": {
    "id": 1,
    "ingredients": [
      {
        "ean": 124,
        "id": 2,
        "image": null,
        "title": "onion"
      }
    ],
    "user": "user@user.com"
  }
}
```

.h3 Step
TODO

API Endpoints
-------------

.h3 GET /ingredient

Returns all ingredients that are currently stored in the database.

.h3 GET /ingredient/<EAN>

Returns the ingredient that matches the given EAN. If it is not stored in the database, it will be fetched from the
Migros API.

.h3 GET /shopping_list

.h3 POST /shopping_list

.h3 GET /inventory

.h3 POST /inventory

.h3 DELETE /inventory

.h3 GET /recipe

.h3 GET /recipe/best

.h3 GET /recipe/<ID>

