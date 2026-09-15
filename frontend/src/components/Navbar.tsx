import { Coffee } from 'lucide-react';
export function Navbar({onChat}:{onChat:()=>void}) { return <nav><a className="brand" href="#top"><Coffee size={21}/> CafeAI</a><div className="navlinks"><a href="#menu">Menu</a><a href="#features">Features</a><a href="#about">About</a></div><button className="button small" onClick={onChat}>Chat With CafeAI</button></nav>; }
