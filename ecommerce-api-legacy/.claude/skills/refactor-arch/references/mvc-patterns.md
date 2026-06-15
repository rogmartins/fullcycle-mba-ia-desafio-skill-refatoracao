# MVC Patterns by Framework

Loaded at the start of Phase 3. Consult the section matching the framework identified in the Preconditions.

---

## Canonical MVC Directory Structure

```
project/
├── models/          # data access + business rules
├── views/           # presentation templates only
├── controllers/     # orchestration: receive → call model → return response
└── config/          # env vars, DB config, no secrets in source
```

---

## Ruby / Sinatra

### Directory layout
```
app/
├── models/
│   └── user.rb
├── views/
│   └── users/
│       ├── index.erb
│       └── show.erb
├── controllers/
│   └── users_controller.rb
└── config/
    └── database.rb
```

### Model (ActiveRecord or Sequel)
```ruby
# models/user.rb
class User < ActiveRecord::Base
  validates :email, presence: true, uniqueness: true

  def self.active
    where(active: true)
  end
end
```

### Controller (Sinatra)
```ruby
# controllers/users_controller.rb
get '/users' do
  @users = User.active
  erb :'users/index'
end

post '/users' do
  user = User.new(params[:user])
  if user.save
    redirect '/users'
  else
    @errors = user.errors.full_messages
    erb :'users/new'
  end
end
```

### View
```erb
<!-- views/users/index.erb -->
<% @users.each do |user| %>
  <p><%= user.name %></p>
<% end %>
```

### Anti-patterns to eliminate
- SQL in `.erb` files → move to Model
- Business logic in route blocks → extract to Model method
- Hardcoded DB URL in route file → move to `config/database.rb` + `ENV`

---

## Ruby on Rails

Rails enforces MVC natively. Common smells and fixes:

| Smell | Fix |
|-------|-----|
| Fat controller action | Extract to Service Object or Model method |
| Logic in view helper | Move to Presenter or Decorator |
| N+1 in controller | Add `includes(:association)` |
| Raw SQL in controller | Scope on Model |

```ruby
# BAD — controller
def index
  @orders = Order.all
  @total = @orders.sum { |o| o.items.sum(&:price) }
end

# GOOD — model scope + counter cache
def index
  @orders = Order.with_totals
end
```

---

## Python / Flask

### Directory layout
```
app/
├── models/
│   └── user.py
├── views/
│   └── templates/
│       └── users/
│           └── index.html
├── controllers/
│   └── users.py        # Blueprint
└── config.py
```

### Model (SQLAlchemy)
```python
# models/user.py
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    @classmethod
    def active(cls):
        return cls.query.filter_by(active=True).all()
```

### Controller (Blueprint)
```python
# controllers/users.py
from flask import Blueprint, render_template, redirect, url_for
from models.user import User

users_bp = Blueprint('users', __name__)

@users_bp.route('/users')
def index():
    users = User.active()
    return render_template('users/index.html', users=users)
```

### Config (no hardcoded credentials)
```python
# config.py
import os
DATABASE_URL = os.environ['DATABASE_URL']
SECRET_KEY = os.environ['SECRET_KEY']
```

---

## Python / Django

Django is MVT (Model-View-Template) but maps directly:

| Django | MVC equivalent |
|--------|---------------|
| Model  | Model         |
| View   | Controller    |
| Template | View        |

```python
# models.py
class Order(models.Model):
    class Meta:
        app_label = 'orders'

    @classmethod
    def with_customer(cls):
        return cls.objects.select_related('customer')  # fix N+1

# views.py (controller role)
def order_list(request):
    orders = Order.with_customer()
    return render(request, 'orders/list.html', {'orders': orders})
```

---

## PHP / Laravel

### Directory layout
```
app/
├── Models/
│   └── User.php
├── Http/
│   └── Controllers/
│       └── UserController.php
├── Views/           # resources/views/
│   └── users/
│       └── index.blade.php
└── config/
    └── database.php   # reads env(), never hardcoded
```

### Model (Eloquent)
```php
// app/Models/User.php
class User extends Model
{
    protected $fillable = ['name', 'email'];

    public function scopeActive($query)
    {
        return $query->where('active', true);
    }
}
```

### Controller
```php
// app/Http/Controllers/UserController.php
class UserController extends Controller
{
    public function index()
    {
        $users = User::active()->get();
        return view('users.index', compact('users'));
    }
}
```

### Config (no hardcoded credentials)
```php
// config/database.php
'password' => env('DB_PASSWORD'),
```

---

## Go / net/http (or Gin)

### Directory layout
```
internal/
├── models/
│   └── user.go
├── handlers/        # controller equivalent
│   └── user_handler.go
├── views/
│   └── templates/
│       └── users.html
└── config/
    └── config.go    # reads os.Getenv
```

### Model
```go
// internal/models/user.go
type User struct {
    ID    int
    Email string
}

func ActiveUsers(db *sql.DB) ([]User, error) {
    rows, err := db.Query("SELECT id, email FROM users WHERE active = true")
    // scan rows...
}
```

### Handler (controller)
```go
// internal/handlers/user_handler.go
func ListUsers(db *sql.DB) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        users, err := models.ActiveUsers(db)
        if err != nil {
            http.Error(w, "internal error", 500)
            return
        }
        renderTemplate(w, "users.html", users)
    }
}
```

---

## Node.js / Express

### Directory layout
```
src/
├── models/
│   └── user.js
├── controllers/
│   └── userController.js
├── views/
│   └── users/
│       └── index.ejs
└── config/
    └── db.js       # reads process.env
```

### Model (Sequelize or Mongoose)
```js
// models/user.js
const User = sequelize.define('User', {
  email: { type: DataTypes.STRING, unique: true }
});

User.findActive = () => User.findAll({ where: { active: true } });
module.exports = User;
```

### Controller
```js
// controllers/userController.js
const User = require('../models/user');

exports.index = async (req, res) => {
  const users = await User.findActive();
  res.render('users/index', { users });
};
```

---

## Universal Rules (all frameworks)

1. **Models**: own all database access and business rules. No HTTP references.
2. **Controllers**: call models, build response. No SQL. No HTML strings.
3. **Views**: display data only. No queries. No business rules.
4. **Config**: read from environment variables. Never hardcode credentials.
5. **One responsibility per file**: if a file does more than one of the above, split it.
