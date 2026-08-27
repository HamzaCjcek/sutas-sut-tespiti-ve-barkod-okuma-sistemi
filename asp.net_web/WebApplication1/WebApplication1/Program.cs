using WebApplication1.Services;

var projectRoot = Path.GetFullPath(
    Path.Combine(AppContext.BaseDirectory, "..", "..", "..")
);

var builder = WebApplication.CreateBuilder(
    new WebApplicationOptions
    {
        Args = args,
        ContentRootPath = projectRoot,
        WebRootPath = Path.Combine(projectRoot, "wwwroot")
    }
);

builder.Services.AddControllersWithViews();

builder.Services.AddHttpClient<IPythonApiService, PythonApiService>(
    client =>
    {
        client.BaseAddress =
            new Uri("http://127.0.0.1:8000");
    }
);

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

// Şimdilik HTTP kullanıyoruz.
// HTTPS port uyarısını da kaldırır.
// app.UseHttpsRedirection();

app.UseStaticFiles();

app.UseRouting();

app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}"
);

app.Run();