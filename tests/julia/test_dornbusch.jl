using Test
using MacroAIComp

@testset "Dornbusch Tests" begin
    @testset "Steady State Default Calibration" begin
        params = default_calibration(DornbuschParams)
        ss = steady_state(params)

        @test ss["p"] ≈ 1.5 atol=1e-4
        @test ss["s"] ≈ 76.515 atol=1e-4
        @test ss["i"] ≈ 3.0 atol=1e-4
        @test ss["yd"] ≈ 2000.0 atol=1e-4
        @test ss["dp"] ≈ 0.0 atol=1e-4
        @test ss["ds"] ≈ 0.0 atol=1e-4
    end

    @testset "Eigenvalues & Stability" begin
        params = default_calibration(DornbuschParams)
        lambdas = eigenvalues(params)
        sorted_lambdas = sort(lambdas)

        @test sorted_lambdas[1] ≈ -0.7415 atol=1e-4
        @test sorted_lambdas[2] ≈ 0.5395 atol=1e-4
        @test is_saddle_path(params) === true
    end

    @testset "Monetary Shock Simulation" begin
        params = default_calibration(DornbuschParams)
        z_initial = [500.0, 100.0, 2000.0, 3.0, 0.0]
        z_final = [500.0, 101.0, 2000.0, 3.0, 0.0]

        res = simulate_shock(params, z_initial, z_final, 30, 1)

        # Pre-shock (t=0, index 1)
        @test res["p"][1] ≈ 1.5 atol=1e-4
        @test res["s"][1] ≈ 76.515 atol=1e-4
        @test res["i"][1] ≈ 3.0 atol=1e-4

        # Shock period (t=1, index 2)
        # Prices are sticky
        @test res["p"][2] ≈ 1.5 atol=1e-4
        # Exchange rate jumps (overshooting)
        @test res["s"][2] ≈ 80.215 atol=5e-3
        # Interest rate drops
        @test res["i"][2] ≈ 1.0 atol=1e-4

        # Long-run convergence (t=29, index 30)
        @test res["p"][end] ≈ 2.5 atol=1e-2
        @test res["s"][end] ≈ 77.515 atol=1e-2
        @test res["i"][end] ≈ 3.0 atol=1e-2
    end
end
