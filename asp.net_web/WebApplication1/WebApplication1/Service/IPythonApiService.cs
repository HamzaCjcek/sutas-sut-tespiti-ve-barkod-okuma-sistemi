using Microsoft.AspNetCore.Http;

namespace WebApplication1.Services
{
	public interface IPythonApiService
	{
		Task<string> GetStatusAsync();

		Task<string> AnalyzeImageAsync(IFormFile image);
	}
}