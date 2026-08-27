using Microsoft.AspNetCore.Mvc;
using WebApplication1.Services;

namespace WebApplication1.Controllers
{
    public class HomeController : Controller
    {
        private readonly IPythonApiService _pythonApiService;


        public HomeController(
            IPythonApiService pythonApiService
        )
        {
            _pythonApiService = pythonApiService;
        }


        public IActionResult Index()
        {
            return View();
        }


        [HttpGet]
        public async Task<IActionResult> TestPythonApi()
        {
            var result =
                await _pythonApiService.GetStatusAsync();

            return Content(
                result,
                "application/json"
            );
        }


        [HttpPost]
        public async Task<IActionResult> TestPythonAnalyze(
            IFormFile image
        )
        {
            if (image == null || image.Length == 0)
            {
                return BadRequest(
                    "Görsel gönderilmedi."
                );
            }


            var result =
                await _pythonApiService
                    .AnalyzeImageAsync(image);


            return Content(
                result,
                "application/json"
            );
        }
    }
}