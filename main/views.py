from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

Usuario = get_user_model()


def inicio(request):
    return render(request, "inicio.html")


def login(request):
    if request.method == "POST":
        email_input = request.POST.get("email")
        password = request.POST.get("password")
        remember = request.POST.get("remember")

        if not email_input or not password:
            return render(
                request,
                "login.html",
                {
                    "errorCredenciales": "Debes ingresar tu correo electrónico y contraseña."
                },
            )

        user = authenticate(request, username=email_input, password=password)

        if user is not None:
            if remember:
                request.session.set_expiry(1209600)
            else:
                request.session.set_expiry(0)
            auth_login(request, user)
            return redirect("/")
        else:
            return render(
                request,
                "login.html",
                {"errorCredenciales": "Verifica tu correo electrónico y contraseña."},
            )

    return render(request, "login.html")


def registro(request):
    if request.method == "GET":
        return render(request, "registro.html")

    if request.POST.get("password") != request.POST.get("passwordrepeat"):
        return render(
            request, "registro.html", {"errorPassword": "Las contraseñas no coinciden"}
        )

    if Usuario.objects.filter(username=request.POST.get("username")).exists():
        return render(
            request,
            "registro.html",
            {"errorUsername": "El nombre de usuario ya está en uso"},
        )

    if Usuario.objects.filter(email=request.POST.get("email")).exists():
        return render(
            request, "registro.html", {"errorEmail": "El correo ya está en uso"}
        )

    try:
        nuevo_usuario = Usuario.objects.create_user(
            username=request.POST["username"],
            email=request.POST["email"],
            password=request.POST["password"],
        )
        nuevo_usuario.backend = "main.backends.EmailBackend"
        auth_login(request, nuevo_usuario)
        return redirect("/")

    except Exception as e:
        print(f"Error during user creation: {e}")

        return render(
            request,
            "registro.html",
            {"error": "Ocurrió un error inesperado al crear el usuario."},
        )


def cerrar_sesion(request):
    logout(request)
    return redirect("/login")
