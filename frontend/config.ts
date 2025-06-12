interface Config {
  apiBaseUrl: string;
}

const config: Config = {
  // Force localhost for development - change this for production deployment
  apiBaseUrl: "http://164.92.184.138:8000"
};

export default config;