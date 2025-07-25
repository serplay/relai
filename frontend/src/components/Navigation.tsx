import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Bot, Home } from 'lucide-react';

export default function Navigation() {
  const location = useLocation();

  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 hidden md:flex">
          <Link to="/" className="mr-6 flex items-center space-x-2">
            <Home className="h-6 w-6" />
            <span className="hidden font-bold sm:inline-block">
              RelAI
            </span>
          </Link>
        </div>
        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <nav className="flex items-center space-x-2">
            <Link to="/">
              <Button 
                variant={location.pathname === "/" ? "default" : "ghost"}
                size="sm"
              >
                <Home className="h-4 w-4 mr-2" />
                Task Manager
              </Button>
            </Link>
            <Link to="/slack-bot">
              <Button 
                variant={location.pathname === "/slack-bot" ? "default" : "ghost"}
                size="sm"
              >
                <Bot className="h-4 w-4 mr-2" />
                Slack Bot
              </Button>
            </Link>
          </nav>
        </div>
      </div>
    </nav>
  );
} 