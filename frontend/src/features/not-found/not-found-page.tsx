import React from 'react';
import { Link } from 'react-router-dom';
import { Home } from 'lucide-react';
import { Button } from '@/components/ui/button';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F7FAF9] p-6 text-[#172825]">
      <div className="max-w-md w-full p-8 rounded-[6px] bg-white border border-[#DCE6E2] shadow-subtle text-center space-y-5">
        <div className="h-12 w-12 rounded-[4px] bg-[#EEF8F7] border border-[#BDCEC8] text-[#123E40] font-mono font-bold text-xl flex items-center justify-center mx-auto">
          404
        </div>
        <div>
          <h1 className="text-xl font-bold text-[#172825]">Route Not Found</h1>
          <p className="text-xs text-[#40524E] mt-2 leading-relaxed">
            The requested academic resource or navigation path does not exist on this institutional platform.
          </p>
        </div>
        <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link to="/" className="w-full sm:w-auto">
            <Button variant="outline" size="sm" className="w-full gap-1.5 border-[#BDCEC8]">
              <Home className="h-3.5 w-3.5" />
              <span>Landing Page</span>
            </Button>
          </Link>
          <Link to="/app/dashboard" className="w-full sm:w-auto">
            <Button variant="primary" size="sm" className="w-full gap-1.5">
              <span>Back to Workspace</span>
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};
