interface InternalWeather {
    temperature: number;
    windspeed: number;
    observationTime: Date;
    stationId: number;
};

interface RawWeatherResponse {
    latitude: number;
    longitude: number;
    generationtime_ms: number;
    utc_offset_seconds: number;
    timezone: string;
    timezone_abbreviation: string;
    elevation: number;
    current_weather_units: {
        time: string;
        interval: string;
        temperature: string;
        windspeed: string;
        winddirection: string;
        is_day: string;
        weathercode: string;
    };
    current_weather: {
        time: string;
        interval: number;
        temperature: number;
        windspeed: number;
        winddirection: number;
        is_day: number;
        weathercode: number;
    };
};

interface GetCurrentWeatherInput {
    latitude: number | string;
    longitude: number | string;
}

class WeatherClient {
    baseUrl = new URL("https://api.open-meteo.com/v1/forecast");

    async getCurrentWeather({
        latitude,
        longitude
    }: GetCurrentWeatherInput): Promise<InternalWeather | null> {
        const url = new URL(this.baseUrl);
        url.searchParams.set("current_weather", "true");
        url.searchParams.set("latitude", latitude.toString());
        url.searchParams.set("longitude", longitude.toString());

        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error("HTTP Error");

            const body = await response.json() as RawWeatherResponse;
            const curr = body.current_weather

            return {
                stationId: 1,
                temperature: curr.temperature,
                windspeed: curr.windspeed,
                observationTime: new Date(curr.time),
            }
        } catch (e) {
            console.log("Failed to get current weather", e);
            return null;
        }
    }
}

async function main() {
    const client = new WeatherClient();

    const referenceLat = 52.52
    const referenceLong = 13.41

    const sataliteLat = 52.53
    const sataliteLong = 13.42

    const body = await client.getCurrentWeather({
        latitude: sataliteLat,
        longitude: sataliteLong,
    });

    console.log(body);
}

main();
