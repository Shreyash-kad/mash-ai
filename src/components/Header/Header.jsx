function Header() {
    return (
        <header className="app-topbar">
            <div className="window-controls" aria-hidden="true">
                <span className="window-control window-control-close" />
                <span className="window-control window-control-minimize" />
                <span className="window-control window-control-expand" />
            </div>

            <div className="brand-lockup">
                <span className="brand-mark">M</span>
                <div>
                    <h1>Mash AI</h1>
                    <p>Intelligent workspace</p>
                </div>
            </div>
        </header>
    );
}

export default Header;