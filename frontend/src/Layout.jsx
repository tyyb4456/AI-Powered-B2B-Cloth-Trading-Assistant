import React, { useState } from "react";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import ToastContainer from "./components/ToastContainer";
import { Outlet } from "react-router-dom";

export default function Layout() {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    
    return (
        <div className="min-h-screen bg-gray-900">
            <Header 
                sidebarOpen={sidebarOpen} 
                setSidebarOpen={setSidebarOpen} 
            />
            
            <div className="flex">
                <Sidebar 
                    isOpen={sidebarOpen} 
                    setSidebarOpen={setSidebarOpen} 
                />
                
                <main className={`flex-1 transition-all duration-300 ${
                    sidebarOpen ? 'ml-64' : 'ml-16'
                } pt-16`}>
                    <div className="p-6 text-gray-100">
                        <Outlet />
                    </div>
                </main>
            </div>
            
            {/* Toast notifications */}
            <ToastContainer />
        </div>
    );
}