using Microsoft.AspNetCore.Http;

namespace WebApplication1.Services
{
    public class PythonApiService : IPythonApiService
    {
        private readonly HttpClient _httpClient;

        public PythonApiService(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }


        public async Task<string> GetStatusAsync()
        {
            var response = await _httpClient.GetAsync("/");

            response.EnsureSuccessStatusCode();

            return await response.Content.ReadAsStringAsync();
        }


        public async Task<string> AnalyzeImageAsync(IFormFile image)
        {
            using MultipartFormDataContent formData =
                new MultipartFormDataContent();

            using StreamContent fileContent =
                new StreamContent(
                    image.OpenReadStream()
                );

            formData.Add(
                fileContent,
                "image",
                image.FileName
            );

            var response = await _httpClient.PostAsync(
                "/api/analyze",
                formData
            );

            response.EnsureSuccessStatusCode();

            return await response.Content.ReadAsStringAsync();
        }
    }
}