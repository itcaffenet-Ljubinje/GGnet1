# GGRock Management System

[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

> Enterprise-grade diskless gaming center management system powered by GGRock v0.1.2200.2324-1

A modern React + TypeScript frontend application for managing diskless gaming centers using the GGRock backend system. This application provides real-time monitoring, computer management, session tracking, and boot image deployment capabilities.

## 🚀 Features

- **Real-time Monitoring** - Live updates via WebSocket connections
- **Computer Management** - Monitor and control all gaming PCs
- **Session Management** - Track and manage user gaming sessions
- **Boot Image Management** - Deploy and manage diskless boot images
- **Game Library** - Centralized game installation tracking
- **Network Configuration** - DHCP, DNS, and PXE boot settings
- **Remote Access** - Integrated noVNC for remote desktop support
- **System Metrics** - CPU, memory, disk, and network monitoring
- **User Management** - User accounts and permissions
- **Responsive UI** - Modern, mobile-friendly interface

## 📋 Prerequisites

- **Node.js** 18+ 
- **pnpm** (recommended) or npm/yarn
- **GGRock Backend** v0.1.2200.2324-1 or compatible version
- **Docker** (optional, for containerized deployment)

## 🛠️ Installation

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GGnet1
   ```

2. **Install dependencies**
   ```bash
   pnpm install
   # or
   npm install
   # or
   yarn install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your GGRock backend URL:
   ```env
   VITE_GGROCK_API_URL=http://localhost:5000
   VITE_GGROCK_WS_URL=ws://localhost:5000
   VITE_GGROCK_VNC_URL=http://localhost:6080
   ```

4. **Start development server**
   ```bash
   pnpm dev
   # or
   npm run dev
   ```

   The application will be available at `http://localhost:3000`

### Production Build

```bash
# Build for production
pnpm build

# Preview production build
pnpm preview
```

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

The application will be available at `http://localhost:3000`

### Manual Docker Build

```bash
# Build image
docker build -t ggrock-management:latest .

# Run container
docker run -d \
  -p 3000:80 \
  -e VITE_GGROCK_API_URL=http://your-ggrock-api:5000 \
  --name ggrock-frontend \
  ggrock-management:latest
```

## 📚 Project Structure

```
GGnet1/
├── src/
│   ├── components/          # React components
│   │   ├── ui/             # Reusable UI components (shadcn/ui)
│   │   ├── ComputerGrid.tsx
│   │   ├── SessionManager.tsx
│   │   ├── DashboardStats.tsx
│   │   ├── Layout.tsx
│   │   └── Login.tsx
│   ├── pages/              # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Computers.tsx
│   │   ├── Sessions.tsx
│   │   ├── BootImages.tsx
│   │   ├── Games.tsx
│   │   ├── Network.tsx
│   │   └── Settings.tsx
│   ├── hooks/              # Custom React hooks
│   │   ├── useGGRockAPI.ts
│   │   └── useGGRockWebSocket.ts
│   ├── services/           # API services
│   │   └── ggrock-api.ts
│   ├── types/              # TypeScript type definitions
│   │   └── ggrock.ts
│   ├── lib/                # Utility functions
│   │   └── utils.ts
│   ├── App.tsx             # Main application component
│   ├── main.tsx            # Application entry point
│   └── index.css           # Global styles
├── docker/                 # Docker configuration
│   ├── nginx.conf
│   ├── prometheus/
│   └── grafana/
├── public/                 # Static assets
├── Dockerfile              # Docker build configuration
├── docker-compose.yml      # Docker Compose configuration
├── vite.config.ts          # Vite configuration
├── tailwind.config.js      # Tailwind CSS configuration
├── tsconfig.json           # TypeScript configuration
└── package.json            # Project dependencies
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_GGROCK_API_URL` | GGRock backend API URL | `http://localhost:5000` |
| `VITE_GGROCK_WS_URL` | GGRock WebSocket URL | `ws://localhost:5000` |
| `VITE_GGROCK_VNC_URL` | noVNC server URL | `http://localhost:6080` |
| `VITE_ENABLE_VNC` | Enable VNC remote access | `true` |
| `VITE_ENABLE_GRAFANA` | Enable Grafana integration | `true` |
| `VITE_GRAFANA_URL` | Grafana dashboard URL | `http://localhost:3000` |

### Vite Proxy Configuration

The Vite development server is configured to proxy requests to the GGRock backend:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api/ggrock': {
      target: 'http://localhost:5000',
      changeOrigin: true,
    },
    '/vnc': {
      target: 'http://localhost:6080',
      ws: true,
    },
  },
}
```

## 🎨 UI Components

This project uses [shadcn/ui](https://ui.shadcn.com/) components with Tailwind CSS for a modern, accessible UI:

- **Button** - Various button styles and sizes
- **Card** - Container for content sections
- **Badge** - Status indicators
- **Input** - Form input fields
- **Label** - Form labels
- **Alert** - Alert messages and notifications

## 📡 API Integration

### API Client

The `ggrock-api.ts` service provides a typed API client for all GGRock backend endpoints:

```typescript
import { ggRockAPI } from '@/services/ggrock-api';

// Authentication
await ggRockAPI.authenticate({ username, password });

// Computer management
const computers = await ggRockAPI.getComputers();
await ggRockAPI.rebootComputer(computerId);

// Session management
const sessions = await ggRockAPI.getActiveSessions();
await ggRockAPI.endSession(sessionId);
```

### React Query Hooks

Convenient hooks for data fetching with caching:

```typescript
import { useComputers, useActiveSessions } from '@/hooks/useGGRockAPI';

function MyComponent() {
  const { data: computers, isLoading } = useComputers();
  const { data: sessions } = useActiveSessions();
  // ...
}
```

### WebSocket Connections

Real-time updates via WebSocket:

```typescript
import { useComputerStatusUpdates } from '@/hooks/useGGRockWebSocket';

function MyComponent() {
  const { data, isConnected } = useComputerStatusUpdates();
  // Receives real-time computer status updates
}
```

## 🔐 Authentication

The application uses JWT token-based authentication with automatic token refresh:

1. Login with credentials
2. Token stored in localStorage
3. Automatic token refresh on 401 responses
4. Protected routes require authentication

## 🧪 Development

### Code Structure

- **Components** - Reusable UI components following atomic design
- **Pages** - Top-level route components
- **Hooks** - Custom React hooks for business logic
- **Services** - API clients and external service integrations
- **Types** - TypeScript type definitions
- **Utils** - Helper functions and utilities

### Best Practices

- TypeScript for type safety
- React Query for data fetching and caching
- Custom hooks for reusable logic
- Component composition over inheritance
- Responsive design with Tailwind CSS

## 📊 Monitoring

### Prometheus Integration

System metrics are collected via Prometheus (if enabled):
- API response times
- Computer status metrics
- Session statistics
- System resource usage

### Grafana Dashboards

Pre-configured Grafana dashboards for:
- System overview
- Computer monitoring
- Session analytics
- Network statistics

## 🚧 Roadmap

### Phase 1: Core Integration ✅
- [x] API proxy layer setup
- [x] TypeScript interfaces
- [x] Authentication integration
- [x] Computer management integration

### Phase 2: Monitoring & Remote Access
- [ ] Grafana dashboard embedding
- [ ] noVNC integration
- [ ] Real-time metrics
- [ ] WebSocket optimization

### Phase 3: Advanced Features
- [ ] PXE boot management interface
- [ ] Hardware inventory management
- [ ] Network boot file management
- [ ] User role management

### Phase 4: Polish & Optimization
- [ ] Performance optimization
- [ ] UI/UX improvements
- [ ] Comprehensive testing
- [ ] Production deployment

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **GGRock** by ggCircuit LLC - Enterprise diskless boot system
- **shadcn/ui** - Beautiful and accessible UI components
- **Tailwind CSS** - Utility-first CSS framework
- **React Query** - Powerful data synchronization
- **Vite** - Next generation frontend tooling

## 📞 Support

For support and questions:
- **GGRock Documentation**: Contact ggCircuit LLC
- **Issues**: Create an issue in this repository
- **Email**: info@ggcircuit.com (for GGRock backend support)

## 🔗 Related Links

- [GGRock Official Site](https://ggcircuit.com)
- [React Documentation](https://react.dev)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Vite Documentation](https://vitejs.dev)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

---

**Built with ❤️ for esports centers worldwide**
