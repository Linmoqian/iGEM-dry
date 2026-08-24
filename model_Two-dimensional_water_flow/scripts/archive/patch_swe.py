p = r'D:\AAAProject\IGEM\IGEM-dry\model_Two-dimensional_water_flow\src\swflow\swe.py'
s = open(p, encoding='utf-8').read()
anchor = "def volume(self, st):"
s = s.rstrip() + "


def wind_stress(wind_mps, direction_deg, cd=1.3e-3):
    """Meteorological direction: the direction the wind comes FROM (deg, 0=N, 90=E).
    Returns (tau_x, tau_y) wind stress [N/m^2] (positive towards +x/+y)."""
    theta = np.radians(direction_deg)
    ux = -np.sin(theta)
    uy = -np.cos(theta)
    tau = RHO_AIR * cd * wind_mps ** 2
    return tau * ux, tau * uy
"
open(p, 'w', encoding='utf-8').write(s)
print('appended wind_stress')
