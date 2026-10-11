'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Users,
  Zap,
  Box,
  Settings,
  Activity,
  LogOut,
  FolderOpen,
  Workflow,
  CheckCircle2,
  Megaphone,
  Globe,
  Brain,
  TrendingUp,
  ListTodo,
  Bot,
  Briefcase,
  Image,
  Compass,
  UserCircle2,
  Sparkles,
  ShoppingBag,
  ScanEye,
  Binoculars,
  Tag,
} from 'lucide-react';

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarSeparator,
} from '@/components/ui/sidebar';

const mainNavItems = [
  {
    title: 'Dashboard',
    url: '/admin',
    icon: LayoutDashboard,
  },
  {
    title: 'Round Table',
    url: '/admin/round-table',
    icon: Zap,
  },
  {
    title: 'Agents',
    url: '/admin/agents',
    icon: Users,
  },
  {
    title: 'Catalog',
    url: '/admin/catalog',
    icon: ShoppingBag,
  },
  {
    title: '3D Pipeline',
    url: '/admin/3d-pipeline',
    icon: Box,
  },
  {
    title: 'Asset Library',
    url: '/admin/assets',
    icon: FolderOpen,
  },
  {
    title: 'Imagery',
    url: '/admin/imagery',
    icon: Image,
  },
  {
    title: 'Generation Queue',
    url: '/admin/pipeline',
    icon: Workflow,
  },
  {
    title: 'Social Media',
    url: '/admin/social-media',
    icon: Megaphone,
  },
  {
    title: 'Conversion Intel',
    url: '/admin/conversion',
    icon: TrendingUp,
  },
  {
    title: 'Competitors',
    url: '/admin/competitors',
    icon: Binoculars,
  },
  {
    title: 'Pricing',
    url: '/admin/pricing',
    icon: Tag,
  },
  {
    title: 'Fidelity QA',
    url: '/admin/qa',
    icon: CheckCircle2,
  },
  {
    title: 'Renders Review',
    url: '/admin/renders/review',
    icon: ScanEye,
  },
  {
    title: 'Tasks',
    url: '/admin/tasks',
    icon: ListTodo,
  },
  {
    title: 'Jobs',
    url: '/admin/jobs',
    icon: Briefcase,
  },
  {
    title: 'Journey Analytics',
    url: '/admin/journey-analytics',
    icon: Compass,
  },
  {
    title: 'Brand Mascot',
    url: '/admin/mascot',
    icon: UserCircle2,
  },
  {
    title: 'Elite Studio',
    url: '/admin/elite-studio',
    icon: Sparkles,
  },
];

const deployNavItems = [
  {
    title: 'WordPress',
    url: '/admin/wordpress',
    icon: Globe,
  },
  {
    title: 'HuggingFace',
    url: '/admin/huggingface',
    icon: Brain,
  },
];

const systemNavItems = [
  {
    title: 'Monitoring',
    url: '/admin/monitoring',
    icon: Activity,
  },
  {
    title: 'Autonomous',
    url: '/admin/autonomous',
    icon: Bot,
  },
  {
    title: 'Settings',
    url: '/admin/settings',
    icon: Settings,
  },
];

export function AppSidebar() {
  const pathname = usePathname();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    document.cookie = 'access_token=; path=/; max-age=0';
    window.location.href = '/login';
  };

  return (
    <Sidebar className="border-r border-gray-800 bg-gray-900">
      <SidebarHeader className="border-b border-gray-800 p-4">
        <Link href="/admin" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-rose-400 to-rose-600">
            <span className="text-lg font-bold text-white">DS</span>
          </div>
          <div className="flex flex-col">
            <span className="text-lg font-bold text-white">DevSkyy</span>
            <span className="text-xs text-gray-400">Enterprise AI Platform</span>
          </div>
        </Link>
      </SidebarHeader>

      <SidebarContent className="bg-gray-900">
        <SidebarGroup>
          <SidebarGroupLabel className="text-gray-500">Platform</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainNavItems.map((item) => {
                const isActive = pathname === item.url ||
                  (item.url !== '/admin' && pathname.startsWith(item.url));
                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton
                      asChild
                      isActive={isActive}
                      tooltip={item.title}
                      className={isActive
                        ? 'bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 hover:text-rose-300'
                        : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                      }
                    >
                      <Link href={item.url}>
                        <item.icon className="h-4 w-4" />
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarSeparator className="bg-gray-800" />

        <SidebarGroup>
          <SidebarGroupLabel className="text-gray-500">Deployments</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {deployNavItems.map((item) => {
                const isActive = pathname === item.url ||
                  (pathname.startsWith(item.url));
                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton
                      asChild
                      isActive={isActive}
                      tooltip={item.title}
                      className={isActive
                        ? 'bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 hover:text-rose-300'
                        : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                      }
                    >
                      <Link href={item.url}>
                        <item.icon className="h-4 w-4" />
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarSeparator className="bg-gray-800" />

        <SidebarGroup>
          <SidebarGroupLabel className="text-gray-500">System</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {systemNavItems.map((item) => {
                const isActive = pathname === item.url;
                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton
                      asChild
                      isActive={isActive}
                      tooltip={item.title}
                      className={isActive
                        ? 'bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 hover:text-rose-300'
                        : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                      }
                    >
                      <Link href={item.url}>
                        <item.icon className="h-4 w-4" />
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-gray-800 bg-gray-900 p-4">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              onClick={handleLogout}
              className="text-gray-400 hover:bg-red-500/10 hover:text-red-400"
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
